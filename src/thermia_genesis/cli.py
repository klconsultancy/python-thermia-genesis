"""The ``thermia-genesis`` command: read a pump and write what it holds as JSON.

The command only reads; it never writes to the pump.
"""

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from enum import Enum, Flag
from pathlib import Path
from typing import Any

from modbus_connection import ModbusUnit
from modbus_connection.cli_helper import add_connection_args, connect_from_args
from modbus_connection.exceptions import ModbusConnectionError, ModbusError, ModbusTimeoutError

from thermia_genesis._pump import (
    ENABLE_COILS,
    GROUPS,
    MAX_BLOCK_SIZE,
    MIN_BLOCK_SIZE,
    OPTIONAL_PARTS,
    SUBSYSTEMS,
    ThermiaGenesis,
    read_enable_coil,
)


def _json_value(value: object) -> object:
    """Convert a decoded value to JSON: a flag to its member names, an enum to its name."""
    if isinstance(value, Flag):
        return [member.name for member in value]
    if isinstance(value, Enum):
        return value.name
    return value


async def dump(unit: ModbusUnit, *, max_block_size: int = MAX_BLOCK_SIZE) -> dict[str, Any]:
    """Read every register the pump has and return it raw and decoded.

    A register space whose read fails is left out and listed under ``failed``, keyed like
    ``registers``. A lost connection or a timeout propagates.
    """
    pump = ThermiaGenesis(unit, max_block_size=max_block_size)
    await pump.async_ensure_setup()
    raw: dict[str, dict[int, int | bool]] = {}
    failed: dict[str, str] = {}
    for space, name in GROUPS.items():
        try:
            registers = await getattr(pump, name).async_read_raw(notify=False)
        except (ModbusConnectionError, ModbusTimeoutError):
            raise
        except ModbusError as err:
            failed[space] = str(err)
            continue
        for read_space, by_address in registers.items():
            raw.setdefault(read_space, {}).update(by_address)
    # The Enable coils of absent parts too, so a fixture answers them as the pump does.
    coils = raw.setdefault("coil", {})
    for address in ENABLE_COILS:
        if address not in coils and (enabled := await read_enable_coil(unit, address)) is not None:
            coils[address] = enabled
    values: dict[str, dict[str, object]] = {}
    for name in SUBSYSTEMS:
        subsystem = getattr(pump, name)
        if subsystem is None:
            continue
        values[name] = {
            field: _json_value(getattr(subsystem, field))
            for component in subsystem.components.values()
            for field in component.declared_fields
        }
    firmware = pump.firmware_version
    return {
        "firmware": None if firmware is None else str(firmware),
        "parts": {name: getattr(pump, name) is not None for name in OPTIONAL_PARTS},
        "registers": {
            space: {str(address): registers[address] for address in sorted(registers)}
            for space, registers in raw.items()
        },
        "values": values,
        "failed": failed,
    }


async def _dump_from_args(args: argparse.Namespace) -> dict[str, Any]:
    connection = await connect_from_args(args)
    try:
        return await dump(connection.for_unit(args.unit), max_block_size=args.max_block_size)
    finally:
        await connection.close()


def _block_size(text: str) -> int:
    """Parse ``--max-block-size``: an integer the library accepts."""
    msg = f"must be {MIN_BLOCK_SIZE}-{MAX_BLOCK_SIZE}"
    try:
        size = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(msg) from None
    if not MIN_BLOCK_SIZE <= size <= MAX_BLOCK_SIZE:
        raise argparse.ArgumentTypeError(msg)
    return size


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command; return the exit status."""
    parser = argparse.ArgumentParser(
        prog="thermia-genesis", description="Read a Thermia Genesis heat pump over Modbus."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    dump_parser = commands.add_parser(
        "dump", help="read every register and write JSON (for bug reports and test fixtures)"
    )
    add_connection_args(dump_parser)
    dump_parser.add_argument(
        "--unit", type=int, default=1, help="Modbus unit id (default: 1; ignored on TCP)"
    )
    dump_parser.add_argument(
        "--max-block-size",
        type=_block_size,
        default=MAX_BLOCK_SIZE,
        help=f"most addresses per read, {MIN_BLOCK_SIZE}-{MAX_BLOCK_SIZE} "
        f"(default: {MAX_BLOCK_SIZE}); lower it for a pump that fails on long reads",
    )
    dump_parser.add_argument(
        "-o", "--output", type=Path, default=None, help="write to this file instead of stdout"
    )
    args = parser.parse_args(argv)
    try:
        result = asyncio.run(_dump_from_args(args))
    except ModbusError as err:
        sys.stderr.write(f"thermia-genesis: {err}\n")
        return 1
    text = json.dumps(result, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(text)
    else:
        args.output.write_text(text, encoding="utf-8")
    # The dump is written either way; a space that failed is in it under "failed".
    return 1 if result["failed"] else 0

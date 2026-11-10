"""Run the library over real Modbus TCP against an in-process tmodbus server.

The server replays a captured fixture and refuses every address the fixture doesn't hold,
like a pump that serves only what it has. No hardware is involved.
"""

import asyncio
import json
import socket
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any

import pytest
from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection
from tmodbus.exceptions import IllegalDataAddressError
from tmodbus.pdu import (
    ReadCoilsPDU,
    ReadDiscreteInputsPDU,
    ReadHoldingRegistersPDU,
    ReadInputRegistersPDU,
    WriteSingleCoilPDU,
    WriteSingleRegisterPDU,
)
from tmodbus.server import AsyncTcpServer, ModbusRequestRouter

from thermia_genesis import ThermiaGenesis, cli
from thermia_genesis.v17_1.heat import Heat
from thermia_genesis.v17_1.heat_pump_unit import HeatPumpUnit

REFERENCE_PUMP: dict[str, Any] = json.loads(
    (Path(__file__).parent / "fixtures" / "calibra7-17.1.11.json").read_text(encoding="utf-8")
)

type Request = (
    ReadCoilsPDU | ReadDiscreteInputsPDU | ReadHoldingRegistersPDU | ReadInputRegistersPDU
)


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port: int = probe.getsockname()[1]
        return port


def router_for(registers: dict[str, dict[str, Any]]) -> ModbusRequestRouter:
    """Serve ``registers`` (a fixture's raw registers); refuse any other address.

    A write to a coil or holding register the fixture holds changes ``registers``.
    """
    router = ModbusRequestRouter()

    def serve(space: str) -> Callable[[int, Request], Any]:
        async def handle(_unit_id: int, request: Request) -> list[Any]:
            values = registers.get(space, {})
            addresses = range(request.start_address, request.start_address + request.quantity)
            if any(str(address) not in values for address in addresses):
                raise IllegalDataAddressError(request.function_code)
            return [values[str(address)] for address in addresses]

        return handle

    router.register(ReadCoilsPDU)(serve("coil"))
    router.register(ReadDiscreteInputsPDU)(serve("discrete"))
    router.register(ReadInputRegistersPDU)(serve("input"))
    router.register(ReadHoldingRegistersPDU)(serve("holding"))

    def store(space: str) -> Callable[[int, WriteSingleCoilPDU | WriteSingleRegisterPDU], Any]:
        async def handle(
            _unit_id: int, request: WriteSingleCoilPDU | WriteSingleRegisterPDU
        ) -> Any:  # noqa: ANN401
            if str(request.address) not in registers[space]:
                raise IllegalDataAddressError(request.function_code)
            registers[space][str(request.address)] = request.value
            return request.value

        return handle

    router.register(WriteSingleCoilPDU)(store("coil"))
    router.register(WriteSingleRegisterPDU)(store("holding"))
    return router


async def serve_fixture(registers: dict[str, dict[str, Any]]) -> tuple[AsyncTcpServer, int]:
    port = free_port()
    server = AsyncTcpServer("127.0.0.1", router_for(registers), port=port)
    await server.start()
    return server, port


@pytest.fixture
async def reference_pump() -> AsyncIterator[int]:
    """The port of a server that replays the reference pump."""
    server, port = await serve_fixture(REFERENCE_PUMP["registers"])
    yield port
    await server.stop()


async def test_reads_the_reference_pump_over_tcp(reference_pump: int) -> None:
    connection = ModbusConnection(ModbusTcpParams(host="127.0.0.1", port=reference_pump))
    await connection.connect()
    try:
        unit = connection.for_unit(1)
        pump = ThermiaGenesis(unit)
        report = await pump.async_update()

        assert report.complete
        assert str(pump.firmware_version) == "17.1.11"
        # Every read stays within the fixture, so the server refused nothing.
        assert await cli.dump(unit) == REFERENCE_PUMP
    finally:
        await connection.close()


async def test_dump_command_reads_the_pump_over_tcp(reference_pump: int, tmp_path: Path) -> None:
    output = tmp_path / "pump.json"
    argv = ["dump", "127.0.0.1", "--port", str(reference_pump), "--output", str(output)]

    # The command runs its own event loop, so it runs beside the server's.
    status = await asyncio.to_thread(cli.main, argv)

    assert status == 0
    assert json.loads(output.read_text(encoding="utf-8")) == REFERENCE_PUMP


async def test_leaves_out_a_part_whose_enable_coil_is_refused() -> None:
    # A pump without HGW that refuses its Enable coil (6) instead of reading False.
    registers = {space: dict(values) for space, values in REFERENCE_PUMP["registers"].items()}
    del registers["coil"]["6"]
    server, port = await serve_fixture(registers)
    connection = ModbusConnection(ModbusTcpParams(host="127.0.0.1", port=port))
    try:
        await connection.connect()
        pump = ThermiaGenesis(connection.for_unit(1))
        report = await pump.async_update()

        assert report.complete
        assert pump.hgw is None
        assert pump.cooling is not None
    finally:
        await connection.close()
        await server.stop()


async def test_writes_settings_and_reads_them_back() -> None:
    registers = {space: dict(values) for space, values in REFERENCE_PUMP["registers"].items()}
    server, port = await serve_fixture(registers)
    connection = ModbusConnection(ModbusTcpParams(host="127.0.0.1", port=port))
    try:
        await connection.connect()
        pump = ThermiaGenesis(connection.for_unit(1))
        await pump.async_update()

        await pump.heat.write(Heat.comfort_wheel_setting, 21.5)
        await pump.heat_pump.write(HeatPumpUnit.enable_heat, False)  # noqa: FBT003
        await pump.async_update()

        assert registers["holding"]["5"] == 2150
        assert pump.heat.comfort_wheel_setting == 21.5
        assert pump.heat_pump.enable_heat is False
    finally:
        await connection.close()
        await server.stop()

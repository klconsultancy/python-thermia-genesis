import argparse
import json
from importlib.metadata import entry_points
from pathlib import Path

import pytest
from modbus_connection.exceptions import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusTimeoutError,
)
from modbus_connection.mock import MockModbusConnection, MockModbusUnit, WriteEvent

from thermia_genesis import cli


def reference_pump(unit: MockModbusUnit) -> None:
    """A few values of the reference pump: 17.1.11 with passive cooling only."""
    unit.input[311] = [17, 1, 11]
    unit.input[13] = 905
    unit.input[1] = [99, 1024]
    unit.holding[0] = 3
    unit.coil[33] = True


async def test_dump_holds_the_firmware_parts_registers_and_values(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    reference_pump(mock_modbus_unit)

    dump = await cli.dump(mock_modbus_unit)

    assert dump["firmware"] == "17.1.11"
    assert dump["parts"] == {
        "mix_valve_1": False,
        "hgw": False,
        "cooling": True,
        "pool": False,
        "electric_meter": False,
    }
    assert dump["registers"]["input"]["13"] == 905
    assert dump["registers"]["coil"]["33"] is True
    assert dump["values"]["heat_pump"]["outdoor_temperature"] == 9.05
    assert dump["values"]["status"]["operational_mode"] == "ON_AUTO"
    assert dump["values"]["status"]["running_demands"] == ["NO_DEMAND"]
    assert "pool" not in dump["values"]
    json.dumps(dump)  # serializable as it is


async def test_dump_holds_every_enable_coil(mock_modbus_unit: MockModbusUnit) -> None:
    # Absent parts read nothing else, but a fixture must answer their Enable coils as the
    # pump does: False, not a refusal.
    reference_pump(mock_modbus_unit)

    dump = await cli.dump(mock_modbus_unit)

    coils = dump["registers"]["coil"]
    assert {address: coils[address] for address in ("6", "10", "11", "26", "28", "33")} == {
        "6": False,
        "10": False,
        "11": False,
        "26": False,
        "28": False,
        "33": True,
    }
    assert dump["failed"] == {}


async def test_dump_records_a_space_that_fails(mock_modbus_unit: MockModbusUnit) -> None:
    reference_pump(mock_modbus_unit)
    mock_modbus_unit.fail_read(319, IllegalDataAddressError(), register_type="input")

    dump = await cli.dump(mock_modbus_unit)

    assert list(dump["failed"]) == ["input"]
    assert "input" not in dump["registers"]
    assert dump["values"]["status"]["operational_mode"] == "ON_AUTO"


async def test_dump_stops_on_a_timeout(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.fail_read(0, ModbusTimeoutError(), register_type="holding")

    with pytest.raises(ModbusTimeoutError):
        await cli.dump(mock_modbus_unit)


async def test_dump_never_writes(mock_modbus_unit: MockModbusUnit) -> None:
    writes: list[WriteEvent] = []
    mock_modbus_unit.on_write(writes.append)
    reference_pump(mock_modbus_unit)

    await cli.dump(mock_modbus_unit)

    assert writes == []


@pytest.fixture
def connection(
    monkeypatch: pytest.MonkeyPatch, mock_modbus_connection: MockModbusConnection
) -> MockModbusConnection:
    """Let the CLI connect to the mock connection instead of a real pump."""

    async def connect_from_args(args: argparse.Namespace) -> MockModbusConnection:
        assert args.target == "192.0.2.10"
        return mock_modbus_connection

    monkeypatch.setattr(cli, "connect_from_args", connect_from_args)
    return mock_modbus_connection


@pytest.mark.usefixtures("connection")
def test_main_writes_the_dump_to_a_file(mock_modbus_unit: MockModbusUnit, tmp_path: Path) -> None:
    reference_pump(mock_modbus_unit)
    output = tmp_path / "pump.json"

    assert cli.main(["dump", "192.0.2.10", "--output", str(output)]) == 0

    assert json.loads(output.read_text())["firmware"] == "17.1.11"


@pytest.mark.usefixtures("connection")
def test_main_prints_the_dump(
    mock_modbus_unit: MockModbusUnit, capsys: pytest.CaptureFixture[str]
) -> None:
    reference_pump(mock_modbus_unit)

    assert cli.main(["dump", "192.0.2.10"]) == 0

    assert json.loads(capsys.readouterr().out)["parts"]["cooling"] is True


@pytest.mark.usefixtures("connection")
def test_main_writes_the_dump_but_fails_when_a_space_fails(
    mock_modbus_unit: MockModbusUnit, tmp_path: Path
) -> None:
    reference_pump(mock_modbus_unit)
    mock_modbus_unit.fail_read(319, IllegalDataAddressError(), register_type="input")
    output = tmp_path / "pump.json"

    assert cli.main(["dump", "192.0.2.10", "--output", str(output)]) == 1

    assert list(json.loads(output.read_text())["failed"]) == ["input"]


@pytest.mark.usefixtures("connection")
def test_main_passes_the_maximum_block_size(
    mock_modbus_unit: MockModbusUnit, capsys: pytest.CaptureFixture[str]
) -> None:
    reference_pump(mock_modbus_unit)

    assert cli.main(["dump", "192.0.2.10", "--max-block-size", "16"]) == 0

    assert max(event.count for event in mock_modbus_unit.read_events) <= 16
    assert json.loads(capsys.readouterr().out)["firmware"] == "17.1.11"


@pytest.mark.parametrize("size", ["1", "abc"])
def test_main_refuses_a_block_size_out_of_range(
    capsys: pytest.CaptureFixture[str], size: str
) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["dump", "192.0.2.10", "--max-block-size", size])

    assert exit_info.value.code == 2
    assert "--max-block-size: must be 2-125" in capsys.readouterr().err


def test_main_reports_a_modbus_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def connect_from_args(_args: argparse.Namespace) -> MockModbusConnection:
        message = "no route to host"
        raise ModbusConnectionError(message)

    monkeypatch.setattr(cli, "connect_from_args", connect_from_args)

    assert cli.main(["dump", "192.0.2.10"]) == 1

    assert "no route to host" in capsys.readouterr().err


def test_is_installed_as_a_command() -> None:
    (command,) = entry_points(group="console_scripts", name="thermia-genesis")

    assert command.load() is cli.main

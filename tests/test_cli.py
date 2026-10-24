import argparse
import json
from importlib.metadata import entry_points
from pathlib import Path

import pytest
from modbus_connection.exceptions import ModbusConnectionError
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

"""Replay the captured register dumps of real pumps (tests/fixtures/*.json).

The decoded values in a fixture are what the library read at capture time, so these tests
catch any unintended change in decoding; the errata and the capture itself are where the
values were checked against the pump.
"""

import json
from pathlib import Path
from typing import Any

import pytest
from modbus_connection.mock import MockModbusUnit

from thermia_genesis import ThermiaGenesis
from thermia_genesis.cli import dump

FIXTURES: dict[str, dict[str, Any]] = {
    path.name: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted((Path(__file__).parent / "fixtures").glob("*.json"))
}


def load(unit: MockModbusUnit, fixture: dict[str, Any]) -> None:
    """Serve the fixture's raw registers from the mock unit."""
    stores: dict[str, dict[int, Any]] = {
        "coil": unit.coil,
        "discrete": unit.discrete,
        "input": unit.input,
        "holding": unit.holding,
    }
    for space, registers in fixture["registers"].items():
        for address, value in registers.items():
            stores[space][int(address)] = value


@pytest.mark.parametrize("name", FIXTURES)
async def test_replays_the_fixture(mock_modbus_unit: MockModbusUnit, name: str) -> None:
    fixture = FIXTURES[name]
    load(mock_modbus_unit, fixture)

    replayed = await dump(mock_modbus_unit)

    assert replayed == fixture


def test_has_the_reference_pump() -> None:
    assert "calibra7-17.1.11.json" in FIXTURES


async def test_reference_pump_reads_as_expected(mock_modbus_unit: MockModbusUnit) -> None:
    load(mock_modbus_unit, FIXTURES["calibra7-17.1.11.json"])
    pump = ThermiaGenesis(mock_modbus_unit)

    report = await pump.async_update()

    assert report.complete
    assert str(pump.firmware_version) == "17.1.11"
    assert pump.cooling is not None
    assert pump.cooling.enable_passive_cooling is True
    assert [pump.mix_valve_1, pump.hgw, pump.pool, pump.electric_meter] == [None] * 4

"""The write API: writable fields and ``Subsystem.write``."""

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model import enum, gauge

from thermia_genesis.subsystem import (
    Subsystem,
    at_least,
    between,
    coil,
    holding_register,
    member_of,
)
from thermia_genesis.v17_1.enums import OperationalMode
from thermia_genesis.v17_1.heat import Heat


class Settings(Subsystem):
    """A subsystem with writable settings."""

    enable = coil(9, writable=True)
    set_point = holding_register(gauge(5, 0.01, writable=between(10, 40), unit="°C"))
    limit = holding_register(gauge(125, 0.1, writable=at_least(0), unit="kW"))
    mode = holding_register(enum(0, OperationalMode, writable=member_of(OperationalMode)))
    reading = holding_register(gauge(6, 0.01, unit="°C"))


async def test_write_encodes_the_value_into_its_register(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    await settings.write(Settings.set_point, 22.5)

    assert mock_modbus_unit.holding[5] == 2250


async def test_write_sets_a_coil(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.coil[9] = False
    settings = Settings(mock_modbus_unit)

    await settings.write(Settings.enable, True)  # noqa: FBT003

    assert mock_modbus_unit.coil[9] is True


async def test_write_refuses_a_read_only_field(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(AttributeError, match="read-only"):
        await settings.write(Settings.reading, 22.0)
    assert 6 not in mock_modbus_unit.holding


async def test_write_refuses_a_field_of_another_subsystem(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(
        AttributeError, match="Settings has no field enable_fixed_system_supply_set_point"
    ):
        await settings.write(Heat.enable_fixed_system_supply_set_point, True)  # noqa: FBT003


@pytest.mark.parametrize("value", [9.99, 40.01])
async def test_between_refuses_a_value_out_of_range(
    mock_modbus_unit: MockModbusUnit, value: float
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(ValueError, match=r"set_point must be 10-40, got"):
        await settings.write(Settings.set_point, value)
    assert 5 not in mock_modbus_unit.holding


@pytest.mark.parametrize(("value", "word"), [(10, 1000), (40, 4000)])
async def test_between_includes_its_bounds(
    mock_modbus_unit: MockModbusUnit, value: float, word: int
) -> None:
    settings = Settings(mock_modbus_unit)

    await settings.write(Settings.set_point, value)

    assert mock_modbus_unit.holding[5] == word


async def test_at_least_refuses_a_value_below_its_bound(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(ValueError, match=r"limit must be at least 0, got -0.1"):
        await settings.write(Settings.limit, -0.1)


async def test_at_least_includes_its_bound(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    await settings.write(Settings.limit, 0.0)

    assert mock_modbus_unit.holding[125] == 0


async def test_member_of_writes_a_member(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    await settings.write(Settings.mode, OperationalMode.STANDBY)

    assert mock_modbus_unit.holding[0] == 2


async def test_member_of_refuses_a_value_outside_the_enum(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(ValueError, match="mode must be one of OFF, STANDBY, ON_AUTO, got 7"):
        await settings.write(Settings.mode, 7)  # type: ignore[misc]
    assert 0 not in mock_modbus_unit.holding


def test_writable_tells_which_fields_can_be_written() -> None:
    assert Settings.set_point.writable
    assert Settings.enable.writable
    assert not Settings.reading.writable


def test_assigning_a_writable_field_points_to_write(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(AttributeError, match=r"set_point can't be assigned; use await .*write"):
        settings.set_point = 22.0  # type: ignore[assignment]

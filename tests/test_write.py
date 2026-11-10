"""The write API: writable fields and ``Subsystem.write``."""

import math
from typing import Any

import pytest
from modbus_connection.mock import MockModbusUnit, WriteEvent
from modbus_connection.model import enum, gauge, integer

from thermia_genesis.subsystem import (
    Field,
    Subsystem,
    between,
    coil,
    holding_register,
    input_register,
    member_of,
)
from thermia_genesis.v17_1.enums import OperationalMode
from thermia_genesis.v17_1.heat import Heat


class Settings(Subsystem):
    """A subsystem with writable settings."""

    enable = coil(9, writable=True)
    set_point = holding_register(gauge(5, 0.01, writable=between(10, 40), unit="°C"))
    limit = holding_register(gauge(125, 0.1, writable=between(0, 3276.7), unit="kW"))
    mode = holding_register(enum(0, OperationalMode, writable=member_of(OperationalMode)))
    control = holding_register(integer(124, signed=False, writable=between(0, 3)))
    unchecked = holding_register(gauge(7, 0.1, writable=True))
    reading = holding_register(gauge(6, 0.01, unit="°C"))
    measured = input_register(gauge(12, 0.01, writable=True, unit="°C"))


class MoreSettings(Settings):
    """A later firmware that extends the settings."""


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


async def test_write_refuses_a_value_its_register_cant_hold(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(ValueError, match=r"unchecked .*does not fit"):
        await settings.write(Settings.unchecked, 6553.6)
    assert 7 not in mock_modbus_unit.holding


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
async def test_write_refuses_a_value_that_is_not_finite(
    mock_modbus_unit: MockModbusUnit, value: float
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(ValueError, match="unchecked must be a finite number"):
        await settings.write(Settings.unchecked, value)


@pytest.mark.parametrize(
    ("field", "value", "resolution"),
    [
        (Settings.set_point, 21.555, "0.01"),
        (Settings.limit, 0.04, "0.1"),
        (Settings.control, 2.9, "1"),
    ],
)
async def test_write_refuses_a_value_finer_than_its_register(
    mock_modbus_unit: MockModbusUnit, field: Field[Any], value: float, resolution: str
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(ValueError, match=f"must be a multiple of {resolution}, got {value}"):
        await settings.write(field, value)
    assert mock_modbus_unit.holding == {}


async def test_write_accepts_a_float_that_is_a_whole_multiple(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    settings = Settings(mock_modbus_unit)

    await settings.write(Settings.limit, 0.3)
    await settings.write(Settings.control, 2.0)  # type: ignore[misc]

    assert mock_modbus_unit.holding[125] == 3
    assert mock_modbus_unit.holding[124] == 2


async def test_write_refuses_a_bool_for_a_register(mock_modbus_unit: MockModbusUnit) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(TypeError, match="control takes a number, got True"):
        await settings.write(Settings.control, True)  # noqa: FBT003
    assert 124 not in mock_modbus_unit.holding


async def test_write_refuses_anything_but_a_bool_for_a_coil(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    settings = Settings(mock_modbus_unit)

    with pytest.raises(TypeError, match="enable takes a bool, got 'false'"):
        await settings.write(Settings.enable, "false")  # type: ignore[misc]
    assert 9 not in mock_modbus_unit.coil


def test_input_register_is_never_writable() -> None:
    assert not Settings.measured.writable


async def test_write_sends_nothing_for_a_field_of_another_subsystem(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    writes: list[WriteEvent] = []
    mock_modbus_unit.on_write(writes.append)
    settings = Settings(mock_modbus_unit)

    with pytest.raises(AttributeError):
        await settings.write(Heat.comfort_wheel_setting, 22.0)
    assert writes == []


async def test_field_keeps_its_value_until_the_next_update(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.holding[5] = 2200
    settings = Settings(mock_modbus_unit)
    await settings.components["holding"].async_update()

    await settings.write(Settings.set_point, 21.5)
    assert settings.set_point == 22.0
    await settings.components["holding"].async_update()

    assert settings.set_point == 21.5


async def test_subclass_writes_a_field_it_inherits(mock_modbus_unit: MockModbusUnit) -> None:
    settings = MoreSettings(mock_modbus_unit)

    await settings.write(MoreSettings.set_point, 22.5)

    assert mock_modbus_unit.holding[5] == 2250

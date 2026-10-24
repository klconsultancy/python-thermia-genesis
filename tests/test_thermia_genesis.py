import importlib
import inspect
import pkgutil
from typing import assert_type

import pytest
from modbus_connection.exceptions import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusTimeoutError,
)
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model import gauge
from modbus_connection.model.fields import CoilField, DiscreteInputField

from thermia_genesis import ThermiaGenesis, v17_1
from thermia_genesis.subsystem import Subsystem, input_register
from thermia_genesis.v17_1.cooling import Cooling
from thermia_genesis.v17_1.electric_meter import ElectricMeter
from thermia_genesis.v17_1.enums import OperationalMode
from thermia_genesis.v17_1.heat import Heat, MixValve1
from thermia_genesis.v17_1.pool import Pool
from thermia_genesis.v17_1.tap_water import Hgw

ALWAYS = ["heat_pump", "heat", "tap_water", "status"]
# The Enable coil of each optional part (docs/design.md); cooling has two.
ENABLE_COILS = {
    6: "hgw",
    10: "cooling",
    11: "mix_valve_1",
    26: "electric_meter",
    28: "pool",
    33: "cooling",
}
OPTIONAL = sorted(set(ENABLE_COILS.values()))


def enable_every_part(unit: MockModbusUnit) -> None:
    for address in ENABLE_COILS:
        unit.coil[address] = True


def present(pump: ThermiaGenesis) -> list[Subsystem]:
    subsystems = [getattr(pump, name) for name in ALWAYS + OPTIONAL]
    return [subsystem for subsystem in subsystems if subsystem is not None]


async def test_reads_every_subsystem(mock_modbus_unit: MockModbusUnit) -> None:
    # Values of the reference pump.
    enable_every_part(mock_modbus_unit)
    mock_modbus_unit.holding[0] = 3
    mock_modbus_unit.input[48] = [0, 10777]
    mock_modbus_unit.input[12] = 20000
    mock_modbus_unit.input[15] = 5329
    mock_modbus_unit.input[106] = 2214
    mock_modbus_unit.holding[58] = 2600
    mock_modbus_unit.holding[298] = 0
    mock_modbus_unit.input[45] = 20000
    mock_modbus_unit.discrete[220] = True
    pump = ThermiaGenesis(mock_modbus_unit)

    report = await pump.async_update()

    assert report.complete
    assert pump.status.operational_mode is OperationalMode.ON_AUTO
    assert pump.heat_pump.compressor_operating_hours == 10777
    assert pump.heat.system_supply_line_temperature is None
    assert pump.heat.heating_season_active is True
    assert pump.tap_water.top_temperature == 53.29
    assert pump.cooling is not None
    assert pump.cooling.circuit_supply_line_temperature == 22.14
    assert pump.pool is not None
    assert pump.pool.charge_set_point == 26.0
    assert pump.electric_meter is not None
    assert pump.electric_meter.enable_current_limitation is True
    assert pump.mix_valve_1 is not None
    assert pump.mix_valve_1.enable is True
    assert pump.hgw is not None
    assert pump.hgw.supply_line_temperature is None


def test_fields_are_typed(mock_modbus_unit: MockModbusUnit) -> None:
    # mypy checks these: a field typed as Any fails assert_type.
    pump = ThermiaGenesis(mock_modbus_unit)

    assert_type(pump.heat.system_supply_line_temperature, float | None)
    assert_type(pump.heat_pump.compressor_operating_hours, int | None)
    assert_type(pump.status.operational_mode, OperationalMode | None)
    assert_type(pump.heat.heating_season_active, bool | None)
    assert_type(pump.cooling, Cooling | None)
    assert_type(pump.pool, Pool | None)
    assert_type(pump.electric_meter, ElectricMeter | None)
    assert_type(pump.mix_valve_1, MixValve1 | None)
    assert_type(pump.hgw, Hgw | None)


def mapped_addresses(subsystems: list[Subsystem]) -> set[tuple[str, int]]:
    """Every address the subsystems declare, per register space."""
    addresses = set()
    for subsystem in subsystems:
        for component in subsystem.components.values():
            for field in component.declared_fields.values():
                if isinstance(field, CoilField):
                    addresses.add(("coil", field.address))
                elif isinstance(field, DiscreteInputField):
                    addresses.add(("discrete", field.address))
                else:
                    space = component.register_space
                    addresses |= {(space, field.address + i) for i in range(field.count)}
    return addresses


def read_addresses(unit: MockModbusUnit) -> set[tuple[str, int]]:
    return {
        (event.register_type, event.address + offset)
        for event in unit.read_events
        for offset in range(event.count)
    }


async def test_reads_only_the_mapped_addresses(mock_modbus_unit: MockModbusUnit) -> None:
    # Another pump or firmware may refuse an address the document doesn't list, so no read
    # bridges a gap between mapped registers.
    enable_every_part(mock_modbus_unit)
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert read_addresses(mock_modbus_unit) == mapped_addresses(present(pump))


async def test_leaves_out_the_parts_that_are_not_enabled(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert [name for name in OPTIONAL if getattr(pump, name) is not None] == []
    enable_coils = {("coil", address) for address in ENABLE_COILS}
    assert read_addresses(mock_modbus_unit) == mapped_addresses(present(pump)) | enable_coils


@pytest.mark.parametrize(("address", "part"), ENABLE_COILS.items())
async def test_detects_a_part_from_its_enable_coil(
    mock_modbus_unit: MockModbusUnit, address: int, part: str
) -> None:
    mock_modbus_unit.coil[address] = True
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert [name for name in OPTIONAL if getattr(pump, name) is not None] == [part]


async def test_detects_the_parts_once(mock_modbus_unit: MockModbusUnit) -> None:
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()
    mock_modbus_unit.coil[28] = True
    await pump.async_update()

    # The pool was enabled after the first update; it shows up after a reload only.
    assert pump.pool is None
    reads_of_coil_28 = [
        event
        for event in mock_modbus_unit.read_events
        if event.register_type == "coil" and event.address <= 28 < event.address + event.count
    ]
    assert len(reads_of_coil_28) == 1


async def test_a_failed_read_stops_only_its_register_space(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.fail_read(48, IllegalDataAddressError(), register_type="input")
    mock_modbus_unit.holding[0] = 3
    mock_modbus_unit.coil[9] = True
    pump = ThermiaGenesis(mock_modbus_unit)

    report = await pump.async_update()

    assert set(report.failed) == {"input_registers"}
    assert report.updated == {"coils", "discrete_inputs", "holding_registers"}
    assert pump.status.operational_mode is OperationalMode.ON_AUTO
    assert pump.heat_pump.enable_heat is True


async def test_raises_when_the_link_is_down(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.fail_read(0, ModbusConnectionError(), register_type="holding")
    pump = ThermiaGenesis(mock_modbus_unit)

    with pytest.raises(ModbusConnectionError):
        await pump.async_update()


async def test_raises_when_nothing_answers(mock_modbus_unit: MockModbusUnit) -> None:
    # The coils are read first; a timeout before anything answered means a dead link.
    mock_modbus_unit.fail_read(3, ModbusTimeoutError(), register_type="coil")
    pump = ThermiaGenesis(mock_modbus_unit)

    with pytest.raises(ModbusTimeoutError):
        await pump.async_update()


def test_has_no_unknown_fields(mock_modbus_unit: MockModbusUnit) -> None:
    pump = ThermiaGenesis(mock_modbus_unit)

    with pytest.raises(AttributeError, match="no_such_field"):
        _ = pump.heat.no_such_field  # type: ignore[attr-defined]


async def test_has_every_subsystem_of_the_map(mock_modbus_unit: MockModbusUnit) -> None:
    enable_every_part(mock_modbus_unit)
    pump = ThermiaGenesis(mock_modbus_unit)
    await pump.async_update()
    declared = set()
    for module_info in pkgutil.iter_modules(v17_1.__path__):
        module = importlib.import_module(f"{v17_1.__name__}.{module_info.name}")
        declared |= {
            member
            for member in vars(module).values()
            if inspect.isclass(member)
            and issubclass(member, Subsystem)
            and member.__module__ == module.__name__
        }

    assert {type(subsystem) for subsystem in present(pump)} == declared


def test_subsystem_class_gives_the_field_declaration() -> None:
    declaration = Heat.system_supply_line_temperature

    assert declaration.space == "input"
    assert declaration.field.address == 12


def test_fields_are_read_only(mock_modbus_unit: MockModbusUnit) -> None:
    # mypy rejects the assignment too; the ignore would be unused otherwise.
    pump = ThermiaGenesis(mock_modbus_unit)

    with pytest.raises(AttributeError, match="read-only"):
        pump.tap_water.top_temperature = 99.0  # type: ignore[assignment]


class HeatWithExtraRegister(Heat):
    """A later firmware that adds a register to heat."""

    extra_temperature = input_register(gauge(500, 0.01))


async def test_subclass_keeps_the_fields_it_inherits(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.input[12] = 2214
    mock_modbus_unit.input[500] = 1234
    heat = HeatWithExtraRegister(mock_modbus_unit)

    for component in heat.components.values():
        await component.async_update()

    assert heat.system_supply_line_temperature == 22.14
    assert heat.extra_temperature == 12.34

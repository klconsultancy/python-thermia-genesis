import importlib
import inspect
import pkgutil

import pytest
from modbus_connection.exceptions import IllegalDataAddressError
from modbus_connection.mock import MockModbusUnit
from modbus_connection.model import Component
from modbus_connection.model.fields import CoilField, DiscreteInputField

from thermia_genesis import Subsystem, ThermiaGenesis, v17_1
from thermia_genesis.v17_1.enums import OperationalMode
from thermia_genesis.v17_1.heat import HeatInputRegisters

SUBSYSTEMS = ["heat_pump", "heat", "tap_water", "cooling", "pool", "electric_meter", "status"]


async def test_reads_every_subsystem(mock_modbus_unit: MockModbusUnit) -> None:
    # Values of the reference pump.
    mock_modbus_unit.holding[0] = 3
    mock_modbus_unit.input[48] = [0, 10777]
    mock_modbus_unit.input[12] = 20000
    mock_modbus_unit.input[15] = 5329
    mock_modbus_unit.input[106] = 2214
    mock_modbus_unit.holding[58] = 2600
    mock_modbus_unit.coil[26] = False
    mock_modbus_unit.discrete[220] = True
    pump = ThermiaGenesis(mock_modbus_unit)

    report = await pump.async_update()

    assert report.complete
    assert pump.status.operational_mode is OperationalMode.ON_AUTO
    assert pump.heat_pump.compressor_operating_hours == 10777
    assert pump.heat.system_supply_line_temperature is None
    assert pump.heat.heating_season_active is True
    assert pump.tap_water.top_temperature == 53.29
    assert pump.cooling.circuit_supply_line_temperature == 22.14
    assert pump.pool.charge_set_point == 26.0
    assert pump.electric_meter.enable_current_limitation is False


def mapped_addresses(pump: ThermiaGenesis) -> set[tuple[str, int]]:
    """Every address the map declares, per register space."""
    addresses = set()
    for subsystem in SUBSYSTEMS:
        for component in getattr(pump, subsystem).components:
            for field in component.declared_fields.values():
                if isinstance(field, CoilField):
                    addresses.add(("coil", field.address))
                elif isinstance(field, DiscreteInputField):
                    addresses.add(("discrete", field.address))
                else:
                    space = component.register_space
                    addresses |= {(space, field.address + i) for i in range(field.count)}
    return addresses


async def test_reads_only_the_mapped_addresses(mock_modbus_unit: MockModbusUnit) -> None:
    # Another pump or firmware may refuse an address the document doesn't list, so no read
    # bridges a gap between mapped registers.
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    read = {
        (event.register_type, event.address + offset)
        for event in mock_modbus_unit.read_events
        for offset in range(event.count)
    }
    assert read == mapped_addresses(pump)


async def test_reports_a_failed_read(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.fail_read(48, IllegalDataAddressError(), register_type="input")
    pump = ThermiaGenesis(mock_modbus_unit)

    report = await pump.async_update()

    assert not report.complete
    assert isinstance(report.failed["registers"], IllegalDataAddressError)


def test_subsystem_has_no_unknown_fields(mock_modbus_unit: MockModbusUnit) -> None:
    pump = ThermiaGenesis(mock_modbus_unit)

    with pytest.raises(AttributeError, match="no_such_field"):
        _ = pump.heat.no_such_field


def test_subsystem_refuses_a_field_name_twice(mock_modbus_unit: MockModbusUnit) -> None:
    components = [HeatInputRegisters(mock_modbus_unit), HeatInputRegisters(mock_modbus_unit)]

    with pytest.raises(ValueError, match="system_supply_line_temperature"):
        Subsystem(components)


def test_exposes_every_field_of_the_map(mock_modbus_unit: MockModbusUnit) -> None:
    pump = ThermiaGenesis(mock_modbus_unit)
    # The subsystem attribute of each module; the heat pump unit is pump.heat_pump.
    attributes = {"heat_pump_unit": "heat_pump"}
    missing = []
    for module_info in pkgutil.iter_modules(v17_1.__path__):
        module = importlib.import_module(f"{v17_1.__name__}.{module_info.name}")
        subsystem = getattr(pump, attributes.get(module_info.name, module_info.name), None)
        for component in vars(module).values():
            if not (
                inspect.isclass(component)
                and issubclass(component, Component)
                and component.__module__ == module.__name__
            ):
                continue
            missing += [
                f"{module_info.name}.{name}"
                for name in component.declared_fields
                if not any(isinstance(c, component) for c in getattr(subsystem, "components", []))
            ]

    assert missing == []

"""The public entry point: a Genesis heat pump on a Modbus unit."""

from collections.abc import Iterable
from typing import Any

from modbus_connection import ModbusUnit
from modbus_connection.model import Component, ComponentGroup, Device, UpdateReport

from thermia_genesis.v17_1 import (
    cooling,
    electric_meter,
    heat,
    heat_pump_unit,
    pool,
    status,
    tap_water,
)


class Subsystem:
    """The fields of one subsystem, whichever register space they are read from."""

    def __init__(self, components: Iterable[Component]) -> None:
        """Raise ``ValueError`` if two components declare the same field name."""
        self._components: dict[str, Component] = {}
        for component in components:
            for name in component.declared_fields:
                if name in self._components:
                    msg = f"field {name!r} is declared twice"
                    raise ValueError(msg)
                self._components[name] = component

    @property
    def components(self) -> list[Component]:
        """The components that hold this subsystem's fields."""
        return list(dict.fromkeys(self._components.values()))

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        try:
            component = self.__dict__["_components"][name]
        except KeyError:
            raise AttributeError(name) from None
        return getattr(component, name)


class ThermiaGenesis(Device):
    """A Thermia heat pump on the Genesis platform, firmware 17.1."""

    def __init__(self, unit: ModbusUnit) -> None:
        super().__init__(unit)
        self.heat_pump = Subsystem(
            [
                heat_pump_unit.HeatPumpUnitCoils(unit),
                heat_pump_unit.HeatPumpUnitDiscreteInputs(unit),
                heat_pump_unit.HeatPumpUnitInputRegisters(unit),
                heat_pump_unit.HeatPumpUnitHoldingRegisters(unit),
            ]
        )
        self.heat = Subsystem(
            [
                heat.HeatCoils(unit),
                heat.HeatDiscreteInputs(unit),
                heat.HeatInputRegisters(unit),
                heat.HeatHoldingRegisters(unit),
            ]
        )
        self.tap_water = Subsystem(
            [
                tap_water.TapWaterCoils(unit),
                tap_water.TapWaterDiscreteInputs(unit),
                tap_water.TapWaterInputRegisters(unit),
                tap_water.TapWaterHoldingRegisters(unit),
            ]
        )
        self.cooling = Subsystem(
            [
                cooling.CoolingCoils(unit),
                cooling.CoolingDiscreteInputs(unit),
                cooling.CoolingInputRegisters(unit),
                cooling.CoolingHoldingRegisters(unit),
            ]
        )
        self.pool = Subsystem(
            [
                pool.PoolCoils(unit),
                pool.PoolDiscreteInputs(unit),
                pool.PoolInputRegisters(unit),
                pool.PoolHoldingRegisters(unit),
            ]
        )
        self.electric_meter = Subsystem(
            [
                electric_meter.ElectricMeterCoils(unit),
                electric_meter.ElectricMeterInputRegisters(unit),
            ]
        )
        self.status = Subsystem(
            [
                status.StatusInputRegisters(unit),
                status.StatusHoldingRegisters(unit),
            ]
        )
        subsystems = (
            self.heat_pump,
            self.heat,
            self.tap_water,
            self.cooling,
            self.pool,
            self.electric_meter,
            self.status,
        )
        components = [component for subsystem in subsystems for component in subsystem.components]
        for component in components:
            # Read only mapped addresses: another pump or firmware may refuse one the document
            # doesn't list, which would fail the whole read.
            component.max_gap = 0
        # One group, so adjacent registers of different subsystems share a read.
        self.registers = ComponentGroup(unit, components)

    async def async_update(self) -> UpdateReport:
        """Read every register of the map and report whether it succeeded."""
        return await self.async_poll(["registers"])

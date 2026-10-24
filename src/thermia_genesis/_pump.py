"""The public entry point: a Genesis heat pump on a Modbus unit."""

from modbus_connection import ModbusUnit
from modbus_connection.model import ComponentGroup, Device, UpdateReport

from thermia_genesis.subsystem import Space, Subsystem
from thermia_genesis.v17_1.cooling import Cooling
from thermia_genesis.v17_1.electric_meter import ElectricMeter
from thermia_genesis.v17_1.heat import Heat
from thermia_genesis.v17_1.heat_pump_unit import HeatPumpUnit
from thermia_genesis.v17_1.pool import Pool
from thermia_genesis.v17_1.status import Status
from thermia_genesis.v17_1.tap_water import TapWater

# The ComponentGroup that reads each register space; also the names in the UpdateReport.
GROUPS: dict[Space, str] = {
    "coil": "coils",
    "discrete": "discrete_inputs",
    "input": "input_registers",
    "holding": "holding_registers",
}


class ThermiaGenesis(Device):
    """A Thermia heat pump on the Genesis platform, firmware 17.1."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Map the pump on ``unit``; nothing is read until ``async_update()``."""
        super().__init__(unit)
        self.heat_pump = HeatPumpUnit(unit)
        self.heat = Heat(unit)
        self.tap_water = TapWater(unit)
        self.cooling = Cooling(unit)
        self.pool = Pool(unit)
        self.electric_meter = ElectricMeter(unit)
        self.status = Status(unit)
        subsystems: list[Subsystem] = [
            self.heat_pump,
            self.heat,
            self.tap_water,
            self.cooling,
            self.pool,
            self.electric_meter,
            self.status,
        ]
        for space, name in GROUPS.items():
            components = [s.components[space] for s in subsystems if space in s.components]
            for component in components:
                # Read only mapped addresses: another pump or firmware may refuse one the
                # document doesn't list, which would fail the whole read.
                component.max_gap = 0
            # One group per register space: adjacent registers of different subsystems share
            # a read, and a failed read stops only its own space.
            setattr(self, name, ComponentGroup(unit, components))

    async def async_update(self) -> UpdateReport:
        """Read every register of the map; the report names each register space.

        Raises ``ModbusConnectionError`` when the link is down and ``ModbusTimeoutError``
        when nothing answers, like ``Device.async_poll``.
        """
        return await self.async_poll(GROUPS.values())

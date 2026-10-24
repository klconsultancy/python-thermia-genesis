"""The public entry point: a Genesis heat pump on a Modbus unit."""

from modbus_connection import ModbusUnit
from modbus_connection.model import Component, ComponentGroup, Device, UpdateReport, coil

from thermia_genesis.subsystem import Space, Subsystem
from thermia_genesis.v17_1.cooling import Cooling
from thermia_genesis.v17_1.electric_meter import ElectricMeter
from thermia_genesis.v17_1.heat import Heat, MixValve1
from thermia_genesis.v17_1.heat_pump_unit import HeatPumpUnit
from thermia_genesis.v17_1.pool import Pool
from thermia_genesis.v17_1.status import Status
from thermia_genesis.v17_1.tap_water import Hgw, TapWater

# The ComponentGroup that reads each register space; also the names in the UpdateReport.
GROUPS: dict[Space, str] = {
    "coil": "coils",
    "discrete": "discrete_inputs",
    "input": "input_registers",
    "holding": "holding_registers",
}


class EnableCoils(Component):
    """The coils that tell which optional parts the installation has (docs/design.md)."""

    hgw = coil(6)
    active_cooling = coil(10)
    mix_valve_1 = coil(11)
    current_limitation = coil(26)
    pool = coil(28)
    passive_cooling = coil(33)


class ThermiaGenesis(Device):
    """A Thermia heat pump on the Genesis platform, firmware 17.1.

    The optional parts (``mix_valve_1``, ``hgw``, ``cooling``, ``pool``,
    ``electric_meter``) are ``None`` until the first ``async_update()`` detects them, and
    stay ``None`` if the pump doesn't have them.
    """

    def __init__(self, unit: ModbusUnit) -> None:
        """Map the pump on ``unit``; nothing is read until ``async_update()``."""
        super().__init__(unit)
        self.heat_pump = HeatPumpUnit(unit)
        self.heat = Heat(unit)
        self.tap_water = TapWater(unit)
        self.status = Status(unit)
        self.mix_valve_1: MixValve1 | None = None
        self.hgw: Hgw | None = None
        self.cooling: Cooling | None = None
        self.pool: Pool | None = None
        self.electric_meter: ElectricMeter | None = None

    async def _async_setup(self) -> None:
        """Detect the optional parts from their Enable coils, once."""
        unit = self.modbus_unit
        enabled = EnableCoils(unit)
        enabled.max_gap = 0  # read only mapped coils
        await enabled.async_update()
        if enabled.mix_valve_1:
            self.mix_valve_1 = MixValve1(unit)
        if enabled.hgw:
            self.hgw = Hgw(unit)
        if enabled.active_cooling or enabled.passive_cooling:
            self.cooling = Cooling(unit)
        if enabled.pool:
            self.pool = Pool(unit)
        if enabled.current_limitation:
            self.electric_meter = ElectricMeter(unit)
        subsystems: list[Subsystem | None] = [
            self.heat_pump,
            self.heat,
            self.mix_valve_1,
            self.tap_water,
            self.hgw,
            self.cooling,
            self.pool,
            self.electric_meter,
            self.status,
        ]
        present = [subsystem for subsystem in subsystems if subsystem is not None]
        for space, name in GROUPS.items():
            components = [s.components[space] for s in present if space in s.components]
            for component in components:
                # Read only mapped addresses: another pump or firmware may refuse one the
                # document doesn't list, which would fail the whole read.
                component.max_gap = 0
            # One group per register space: adjacent registers of different subsystems share
            # a read, and a failed read stops only its own space.
            setattr(self, name, ComponentGroup(unit, components))

    async def async_update(self) -> UpdateReport:
        """Read every register of the parts the pump has; the report names each space.

        The first call detects the optional parts. Raises ``ModbusConnectionError`` when the
        link is down and ``ModbusTimeoutError`` when nothing answers, like
        ``Device.async_poll``.
        """
        return await self.async_poll(GROUPS.values())

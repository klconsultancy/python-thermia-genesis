"""The public entry point: a Genesis heat pump on a Modbus unit."""

import logging

from modbus_connection import ModbusUnit
from modbus_connection.model import (
    Component,
    ComponentGroup,
    Device,
    UpdateReport,
    coil,
    read_optional,
)

from thermia_genesis.firmware import FirmwareVersion
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


_LOGGER = logging.getLogger(__name__)


class EnableCoil(Component):
    """One "Enable ..." coil, placed at its address with ``base_offset``."""

    enabled = coil(0)


async def read_enable_coil(unit: ModbusUnit, address: int) -> bool | None:
    """Read the Enable coil at ``address``; ``None`` if the pump refuses it.

    A refusal (illegal address or function) means the pump doesn't have the part. Any other
    error, such as a lost connection or a timeout, propagates, and the next update retries.
    """
    enable_coil = EnableCoil(unit, base_offset=address)
    if await read_optional(enable_coil) is None:
        _LOGGER.info("The pump refuses Enable coil %d; treating its part as absent", address)
        return None
    return bool(enable_coil.enabled)


# The subsystem attributes of ThermiaGenesis, and the optional ones among them.
SUBSYSTEMS = (
    "heat_pump",
    "heat",
    "mix_valve_1",
    "tap_water",
    "hgw",
    "cooling",
    "pool",
    "electric_meter",
    "status",
)
# Each optional part, its subsystem and its Enable coils: the part is present when one of
# them is on (docs/design.md). Cooling is active (coil 10) or passive (coil 33).
PARTS: dict[str, tuple[type[Subsystem], tuple[int, ...]]] = {
    "mix_valve_1": (MixValve1, (11,)),
    "hgw": (Hgw, (6,)),
    "cooling": (Cooling, (10, 33)),
    "pool": (Pool, (28,)),
    "electric_meter": (ElectricMeter, (26,)),
}
OPTIONAL_PARTS = tuple(PARTS)
ENABLE_COILS = tuple(sorted(address for _, addresses in PARTS.values() for address in addresses))


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
        for name, (subsystem_type, addresses) in PARTS.items():
            # Each coil on its own, so a coil the pump refuses leaves out only its part.
            for address in addresses:
                if await read_enable_coil(unit, address):
                    setattr(self, name, subsystem_type(unit))
                    break
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

    @property
    def firmware_version(self) -> FirmwareVersion | None:
        """The control software version, or ``None`` until an update has read it.

        After a failed read the last value remains, like every field. The 17.1 map is used
        whatever the version; check ``supported`` to warn.
        """
        major = self.heat_pump.software_version_major
        minor = self.heat_pump.software_version_minor
        micro = self.heat_pump.software_version_micro
        if major is None or minor is None or micro is None:
            return None
        return FirmwareVersion(major, minor, micro)

    async def async_update(self) -> UpdateReport:
        """Read every register of the parts the pump has; the report names each space.

        The first call detects the optional parts. Raises ``ModbusConnectionError`` when the
        link is down and ``ModbusTimeoutError`` when nothing answers, like
        ``Device.async_poll``.
        """
        return await self.async_poll(GROUPS.values())

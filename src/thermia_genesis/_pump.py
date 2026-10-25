"""The public entry point: a Genesis heat pump on a Modbus unit."""

import logging

from modbus_connection import ModbusUnit
from modbus_connection.exceptions import IllegalDataAddressError, IllegalFunctionError
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

# The longest read Modbus allows for registers (FC03/FC04); modbus_connection caps bits at it too.
MAX_BLOCK_SIZE = 125

# The ComponentGroup that reads each register space; also the names in the UpdateReport.
GROUPS: dict[Space, str] = {
    "coil": "coils",
    "discrete": "discrete_inputs",
    "input": "input_registers",
    "holding": "holding_registers",
}


_LOGGER = logging.getLogger(__name__)


# A read the pump refuses because it lacks the register, as opposed to a failure.
REFUSALS = (IllegalDataAddressError, IllegalFunctionError)
GROUP_LABELS = {
    "coils": "coil",
    "discrete_inputs": "discrete input",
    "input_registers": "input register",
    "holding_registers": "holding register",
}


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

_SUBSYSTEM_TYPES: tuple[type[Subsystem], ...] = (
    HeatPumpUnit,
    Heat,
    TapWater,
    Status,
    *(subsystem_type for subsystem_type, _ in PARTS.values()),
)
# The shortest read the map allows: its widest field (a 32-bit counter spans two registers).
MIN_BLOCK_SIZE = max(
    getattr(field, "count", 1)
    for subsystem_type in _SUBSYSTEM_TYPES
    for component in subsystem_type.component_types.values()
    for field in component.declared_fields.values()
)
ENABLE_COILS = tuple(sorted(address for _, addresses in PARTS.values() for address in addresses))


class ThermiaGenesis(Device):
    """A Thermia heat pump on the Genesis platform, firmware 17.1.

    The optional parts (``mix_valve_1``, ``hgw``, ``cooling``, ``pool``,
    ``electric_meter``) are ``None`` until the first ``async_update()`` detects them, and
    stay ``None`` if the pump doesn't have them.
    """

    def __init__(self, unit: ModbusUnit, *, max_block_size: int = MAX_BLOCK_SIZE) -> None:
        """Map the pump on ``unit``; nothing is read until ``async_update()``.

        ``max_block_size`` caps the number of addresses one read asks for (2-125). Lower it
        for a pump whose Modbus interface fails on long reads. Raises ``ValueError`` for a
        size below the widest field of the map or above what Modbus allows.
        """
        if not MIN_BLOCK_SIZE <= max_block_size <= MAX_BLOCK_SIZE:
            msg = f"max_block_size must be {MIN_BLOCK_SIZE}-{MAX_BLOCK_SIZE}, got {max_block_size}"
            raise ValueError(msg)
        super().__init__(unit)
        self._max_block_size = max_block_size
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
        present: list[tuple[str, Subsystem]] = [
            (name, subsystem)
            for name in SUBSYSTEMS
            if (subsystem := getattr(self, name)) is not None
        ]
        # Per group, each component with the subsystem it belongs to, to name refused fields.
        self._members: dict[str, list[tuple[str, Component]]] = {}
        for space, name in GROUPS.items():
            self._members[name] = [
                (subsystem_name, subsystem.components[space])
                for subsystem_name, subsystem in present
                if space in subsystem.components
            ]
            components = [component for _, component in self._members[name]]
            for component in components:
                # Read only mapped addresses: another pump or firmware may refuse one the
                # document doesn't list, which would fail the whole read.
                component.max_gap = 0
                component.max_span = self._max_block_size
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
        report = await self.async_poll(GROUPS.values())
        refused = [name for name, err in report.failed.items() if isinstance(err, REFUSALS)]
        for name in refused:
            await self._leave_out_refused_fields(name)
            del report.failed[name]
        if refused:
            await self.async_poll(refused, report)
        return report

    async def _leave_out_refused_fields(self, group: str) -> None:
        """Read each field of ``group`` on its own and leave out those the pump refuses."""
        for subsystem_name, component in self._members[group]:
            kept = []
            for name, field in component.declared_fields.items():
                probe = type(component)(self.modbus_unit)
                probe.restrict_fields([name])
                if await read_optional(probe) is None:
                    _LOGGER.warning(
                        "The pump refuses %s %d (%s.%s); reading it as None",
                        GROUP_LABELS[group],
                        field.address,
                        subsystem_name,
                        name,
                    )
                else:
                    kept.append(name)
            if len(kept) < len(component.declared_fields):
                component.restrict_fields(kept)

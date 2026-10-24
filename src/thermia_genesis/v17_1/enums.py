"""Enumerations from the footnotes of the protocol document."""

from enum import IntEnum, IntFlag


class SmartGridMode(IntEnum):
    """Current Smart Grid mode (footnote *4)."""

    EVU = 1
    NORMAL = 4
    COMFORT = 5
    BOOST = 6


class OutdoorTemperatureSource(IntEnum):
    """Where the pump takes the outdoor temperature from (holding register 117)."""

    PT1000_SENSOR = 0
    BMS = 1


class ImmersionHeater(IntEnum):
    """Enabled immersion heater (footnote *7)."""

    DISABLED = 0
    INTERNAL = 2


class MixValveMode(IntEnum):
    """Selected mode for mixing valve 1 (holding register 298)."""

    HEAT = 0
    COOL = 1
    AUTO = 2


class OperationalMode(IntEnum):
    """Operational mode (footnote *2)."""

    OFF = 1
    STANDBY = 2
    ON_AUTO = 3


class Demand(IntEnum):
    """A running or queued demand (footnote *1)."""

    MANUAL_OPERATION = 1
    DEFROST = 2
    HOT_WATER = 3
    HEAT = 4
    ACTIVE_COOLING = 5
    POOL = 6
    ANTI_LEGIONELLA = 7
    PASSIVE_COOLING = 8
    STANDBY = 98
    NO_DEMAND = 99
    OFF = 100


class RunningDemands(IntFlag):
    """All currently running demands, one bit each (footnote *6; bit 8 is reserved)."""

    MANUAL_OPERATION = 1 << 0
    DEFROST = 1 << 1
    HOT_WATER = 1 << 2
    HEAT = 1 << 3
    ACTIVE_COOLING = 1 << 4
    POOL = 1 << 5
    ANTI_LEGIONELLA = 1 << 6
    PASSIVE_COOLING = 1 << 7
    STANDBY = 1 << 9
    NO_DEMAND = 1 << 10
    OFF = 1 << 11

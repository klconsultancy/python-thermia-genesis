"""Enumerations from the footnotes of the protocol document."""

from enum import IntEnum


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

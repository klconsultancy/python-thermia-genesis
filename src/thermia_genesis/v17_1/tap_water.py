"""Tap water (chapter 6): tap water and HGW (hot gas heat recovery)."""

from modbus_connection.model import gauge, integer, uint32

from thermia_genesis.subsystem import (
    Subsystem,
    coil,
    discrete_input,
    holding_register,
    input_register,
)
from thermia_genesis.v17_1 import ABSENT_SENSOR


class TapWater(Subsystem):
    """Tap water (chapter 6.1)."""

    # Listed only in chapter 6, not in chapter 3; see errata.md.
    enable_hot_gas_pump = coil(14)

    mid_sensor_alarm = discrete_input(50)

    top_temperature = input_register(gauge(15, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    lower_temperature = input_register(gauge(16, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    weighted_temperature = input_register(gauge(17, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    # Chapter 6 also lists register 47 as "HGW mix valve position"; see errata.md.
    valve_position = input_register(integer(47, signed=False, unit="%"))
    operating_hours = input_register(uint32(50, unit="h"))
    desired_gear = input_register(integer(139, signed=False))

    start_temperature = holding_register(gauge(22, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    stop_temperature = holding_register(gauge(23, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    maximum_allowed_gear = holding_register(integer(28, signed=False))
    minimum_allowed_gear = holding_register(integer(29, signed=False))


class Hgw(Subsystem):
    """HGW, hot gas heat recovery (chapter 6.2), an optional part of tap water; coil 6."""

    # Listed only in chapter 6, not in chapter 3; see errata.md.
    enable = coil(6)
    sensor_alarm = discrete_input(52)
    regulation_control_signal = discrete_input(223)
    supply_line_temperature = input_register(gauge(45, 0.01, nan=ABSENT_SENSOR, unit="°C"))

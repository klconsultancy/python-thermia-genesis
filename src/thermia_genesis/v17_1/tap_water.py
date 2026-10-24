"""Tap water (chapter 6): tap water and HGW (hot gas heat recovery)."""

from modbus_connection.model import Component, coil, discrete_input, gauge, integer, uint32

from thermia_genesis.v17_1 import ABSENT_SENSOR


class TapWaterCoils(Component):
    """Coils of tap water and HGW."""

    # Both coils are listed only in chapter 6, not in chapter 3; see errata.md.
    enable_hot_gas_pump = coil(14)
    enable_hgw = coil(6)


class TapWaterDiscreteInputs(Component):
    """Discrete inputs of tap water and HGW."""

    mid_sensor_alarm = discrete_input(50)
    hgw_sensor_alarm = discrete_input(52)
    hgw_regulation_control_signal = discrete_input(223)


class TapWaterInputRegisters(Component):
    """Input registers of tap water and HGW."""

    register_space = "input"

    top_temperature = gauge(15, 0.01, nan=ABSENT_SENSOR, unit="°C")
    lower_temperature = gauge(16, 0.01, nan=ABSENT_SENSOR, unit="°C")
    weighted_temperature = gauge(17, 0.01, nan=ABSENT_SENSOR, unit="°C")
    # Chapter 6 also lists register 47 as "HGW mix valve position"; see errata.md.
    valve_position = integer(47, signed=False, unit="%")
    operating_hours = uint32(50, unit="h")
    desired_gear = integer(139, signed=False)
    hgw_supply_line_temperature = gauge(45, 0.01, nan=ABSENT_SENSOR, unit="°C")


class TapWaterHoldingRegisters(Component):
    """Holding registers of tap water (valid when the tap water mode is Normal)."""

    register_space = "holding"

    start_temperature = gauge(22, 0.01, nan=ABSENT_SENSOR, unit="°C")
    stop_temperature = gauge(23, 0.01, nan=ABSENT_SENSOR, unit="°C")
    maximum_allowed_gear = integer(28, signed=False)
    minimum_allowed_gear = integer(29, signed=False)

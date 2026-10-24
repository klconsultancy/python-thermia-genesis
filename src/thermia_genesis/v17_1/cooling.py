"""Cooling (chapter 7): cooling and the cooling circuit."""

from modbus_connection.model import Component, coil, discrete_input, gauge, integer

from thermia_genesis.v17_1 import ABSENT_SENSOR


class CoolingCoils(Component):
    """Coils of cooling."""

    enable_active_cooling = coil(10)
    enable_passive_cooling = coil(33)


class CoolingDiscreteInputs(Component):
    """Discrete inputs of cooling."""

    # Alarms
    supply_line_sensor_alarm = discrete_input(47)
    circuit_supply_line_temperature_deviation_alarm = discrete_input(67)

    # Signals and states
    external_start_brine_pump = discrete_input(78)
    circuit_circulation_pump_control_signal = discrete_input(236)
    surplus_heat_directional_valve_position = discrete_input(238)
    circuit_regulation_control_signal = discrete_input(240)
    active_cooling_directional_valve_position = discrete_input(242)


class CoolingInputRegisters(Component):
    """Input registers of cooling."""

    register_space = "input"

    circuit_supply_line_temperature = gauge(106, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_opening_degree = integer(137, signed=False, unit="%")
    desired_gear = integer(141, signed=False)


class CoolingHoldingRegisters(Component):
    """Holding registers of cooling."""

    register_space = "holding"

    start_temperature = gauge(105, 0.01, nan=ABSENT_SENSOR, unit="°C")
    stop_temperature = gauge(106, 0.01, nan=ABSENT_SENSOR, unit="°C")
    gear_shift_delay = integer(63, signed=False, unit="min")
    minimum_allowed_gear = integer(87, signed=False)
    maximum_allowed_gear = integer(88, signed=False)

    # Cooling mix valve
    mix_valve_set_point = gauge(30, 0.01, unit="%")
    supply_line_mix_valve_lowest_opening_degree = gauge(49, 0.01, unit="%")
    supply_line_mix_valve_highest_opening_degree = gauge(50, 0.01, unit="%")

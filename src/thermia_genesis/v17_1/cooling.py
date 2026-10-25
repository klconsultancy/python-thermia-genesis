"""Cooling (chapter 7): cooling and the cooling circuit."""

from modbus_connection.model import gauge, integer

from thermia_genesis.subsystem import (
    Subsystem,
    coil,
    discrete_input,
    holding_register,
    input_register,
)
from thermia_genesis.v17_1 import ABSENT_SENSOR


class Cooling(Subsystem):
    """The cooling subsystem."""

    enable_active_cooling = coil(10)
    enable_passive_cooling = coil(33)

    # Alarms
    supply_line_sensor_alarm = discrete_input(47)
    circuit_supply_line_temperature_deviation_alarm = discrete_input(67)

    # Signals and states
    external_start_brine_pump = discrete_input(78)
    circuit_circulation_pump_control_signal = discrete_input(236)
    surplus_heat_directional_valve_position = discrete_input(238)
    circuit_regulation_control_signal = discrete_input(240)
    active_cooling_directional_valve_position = discrete_input(242)

    circuit_supply_line_temperature = input_register(gauge(106, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    mix_valve_opening_degree = input_register(integer(137, signed=False, unit="%"))
    desired_gear = input_register(integer(141, signed=False))

    start_temperature = holding_register(gauge(105, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    stop_temperature = holding_register(gauge(106, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    gear_shift_delay = holding_register(integer(63, signed=False, unit="s"))
    minimum_allowed_gear = holding_register(integer(87, signed=False))
    maximum_allowed_gear = holding_register(integer(88, signed=False))

    # Cooling mix valve
    # A temperature, not % as chapter 3 says: the display's "Gewenste koelaanvoer min."
    # (desired cooling supply minimum); see errata.md.
    mix_valve_set_point = holding_register(gauge(30, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    supply_line_mix_valve_lowest_allowed_opening_degree = holding_register(
        gauge(49, 0.01, unit="%")
    )
    supply_line_mix_valve_highest_allowed_opening_degree = holding_register(
        gauge(50, 0.01, unit="%")
    )

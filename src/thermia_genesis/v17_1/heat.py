"""Heat (chapter 5): the heating system and mix valve 1."""

from modbus_connection.model import enum, gauge, integer

from thermia_genesis.subsystem import (
    Subsystem,
    coil,
    discrete_input,
    holding_register,
    input_register,
)
from thermia_genesis.v17_1 import ABSENT_SENSOR
from thermia_genesis.v17_1.enums import MixValveMode


class Heat(Subsystem):
    """The heating system (chapter 5.1)."""

    enable_fixed_system_supply_set_point = coil(41)

    # Alarms
    system_supply_low_temperature_alarm = discrete_input(24)
    system_supply_line_sensor_alarm = discrete_input(35)
    room_temperature_sensor_alarm = discrete_input(74)

    # Signals and states
    system_circulation_pump_control_signal = discrete_input(211)
    heating_season_active = discrete_input(220)

    # System supply and return
    system_supply_line_temperature = input_register(gauge(12, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    system_supply_line_calculated_set_point = input_register(
        gauge(18, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    system_return_line_temperature = input_register(gauge(27, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    calculated_demand = input_register(gauge(30, 0.01))
    desired_gear = input_register(integer(140, signed=False))

    # Heat curve
    selected_heat_curve_supply_line = input_register(gauge(19, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_1 = input_register(gauge(20, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_2 = input_register(gauge(21, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_3 = input_register(gauge(22, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_4 = input_register(gauge(23, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_5 = input_register(gauge(24, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_6 = input_register(gauge(25, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_x_7 = input_register(gauge(26, 0.01, nan=ABSENT_SENSOR, unit="°C"))

    # Buffer tank
    buffer_tank_temperature = input_register(gauge(41, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    buffer_tank_charge_set_point = input_register(gauge(68, 0.01, nan=ABSENT_SENSOR, unit="°C"))

    # System supply set points
    max_limitation_set_point_curve = holding_register(gauge(3, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    min_limitation_set_point_curve = holding_register(gauge(4, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    comfort_wheel_setting = holding_register(gauge(5, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heating_season_stop_temperature = holding_register(
        gauge(16, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    fixed_system_supply_set_point = holding_register(gauge(116, 0.01, nan=ABSENT_SENSOR, unit="°C"))

    # Heat curve
    heat_curve_y_1 = holding_register(gauge(6, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_y_2 = holding_register(gauge(7, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_y_3 = holding_register(gauge(8, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_y_4 = holding_register(gauge(9, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_y_5 = holding_register(gauge(10, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_y_6 = holding_register(gauge(11, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    heat_curve_y_7 = holding_register(gauge(12, 0.01, nan=ABSENT_SENSOR, unit="°C"))


class MixValve1(Subsystem):
    """Mix valve 1 (chapter 5.2), an optional part of heat; enabled by coil 11."""

    enable = coil(11)
    enable_outdoor_temperature_dependent_cooling = coil(37)
    enable_internal_brine_pump_when_cooling = coil(38)

    # Alarms
    supply_line_sensor_alarm = discrete_input(36)
    supply_temperature_deviation_alarm = discrete_input(60)

    # Signals and states
    circulation_pump_control_signal = discrete_input(209)
    producing_passive_cooling = discrete_input(245)

    supply_line_temperature = input_register(gauge(40, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    position = input_register(gauge(43, 0.01, unit="%"))
    desired_temperature = input_register(gauge(147, 0.01, nan=ABSENT_SENSOR, unit="°C"))

    mode = holding_register(enum(298, MixValveMode))
    min_limitation_set_point_curve = holding_register(
        gauge(107, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    max_limitation_set_point_curve = holding_register(
        gauge(108, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    curve_y_1 = holding_register(gauge(109, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    curve_y_2 = holding_register(gauge(110, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    curve_y_3 = holding_register(gauge(111, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    curve_y_4 = holding_register(gauge(112, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    curve_y_5 = holding_register(gauge(113, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    curve_y_6 = holding_register(gauge(114, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    curve_y_7 = holding_register(gauge(115, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    passive_cooling_supply_set_point = holding_register(
        gauge(302, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    cooling_minimum_outdoor_temperature = holding_register(
        gauge(303, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )

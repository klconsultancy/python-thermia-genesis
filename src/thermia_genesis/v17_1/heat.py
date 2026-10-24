"""Heat (chapter 5): the heating system and mix valve 1."""

from modbus_connection.model import Component, coil, discrete_input, enum, gauge, integer

from thermia_genesis.v17_1 import ABSENT_SENSOR
from thermia_genesis.v17_1.enums import MixValveMode


class HeatCoils(Component):
    """Coils of the heating system."""

    enable_mix_valve_1 = coil(11)
    enable_outdoor_temperature_dependent_cooling_mix_valve_1 = coil(37)
    enable_internal_brine_pump_when_cooling_mix_valve_1 = coil(38)
    enable_fixed_system_supply_set_point = coil(41)


class HeatDiscreteInputs(Component):
    """Discrete inputs of the heating system."""

    # Alarms
    system_supply_low_temperature_alarm = discrete_input(24)
    system_supply_line_sensor_alarm = discrete_input(35)
    mix_valve_1_supply_line_sensor_alarm = discrete_input(36)
    mix_valve_1_supply_temperature_deviation_alarm = discrete_input(60)
    room_temperature_sensor_alarm = discrete_input(74)

    # Signals and states
    mix_valve_1_circulation_pump_control_signal = discrete_input(209)
    system_circulation_pump_control_signal = discrete_input(211)
    heating_season_active = discrete_input(220)
    mix_valve_1_producing_passive_cooling = discrete_input(245)


class HeatInputRegisters(Component):
    """Input registers of the heating system."""

    register_space = "input"

    # System supply and return
    system_supply_line_temperature = gauge(12, 0.01, nan=ABSENT_SENSOR, unit="°C")
    system_supply_line_calculated_set_point = gauge(18, 0.01, nan=ABSENT_SENSOR, unit="°C")
    system_return_line_temperature = gauge(27, 0.01, nan=ABSENT_SENSOR, unit="°C")
    calculated_demand = gauge(30, 0.01)
    desired_gear = integer(140, signed=False)

    # Heat curve
    selected_heat_curve_supply_line = gauge(19, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_1 = gauge(20, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_2 = gauge(21, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_3 = gauge(22, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_4 = gauge(23, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_5 = gauge(24, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_6 = gauge(25, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_x_7 = gauge(26, 0.01, nan=ABSENT_SENSOR, unit="°C")

    # Buffer tank
    buffer_tank_temperature = gauge(41, 0.01, nan=ABSENT_SENSOR, unit="°C")
    buffer_tank_charge_set_point = gauge(68, 0.01, nan=ABSENT_SENSOR, unit="°C")

    # Mix valve 1
    mix_valve_1_supply_line_temperature = gauge(40, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_position = gauge(43, 0.01, unit="%")
    mix_valve_1_desired_temperature = gauge(147, 0.01, nan=ABSENT_SENSOR, unit="°C")


class HeatHoldingRegisters(Component):
    """Holding registers of the heating system."""

    register_space = "holding"

    # System supply set points
    max_limitation_set_point_curve = gauge(3, 0.01, nan=ABSENT_SENSOR, unit="°C")
    min_limitation_set_point_curve = gauge(4, 0.01, nan=ABSENT_SENSOR, unit="°C")
    comfort_wheel_setting = gauge(5, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heating_season_stop_temperature = gauge(16, 0.01, nan=ABSENT_SENSOR, unit="°C")
    fixed_system_supply_set_point = gauge(116, 0.01, nan=ABSENT_SENSOR, unit="°C")

    # Heat curve
    heat_curve_y_1 = gauge(6, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_y_2 = gauge(7, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_y_3 = gauge(8, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_y_4 = gauge(9, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_y_5 = gauge(10, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_y_6 = gauge(11, 0.01, nan=ABSENT_SENSOR, unit="°C")
    heat_curve_y_7 = gauge(12, 0.01, nan=ABSENT_SENSOR, unit="°C")

    # Mix valve 1
    mix_valve_1_mode = enum(298, MixValveMode)
    mix_valve_1_min_limitation_set_point_curve = gauge(107, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_max_limitation_set_point_curve = gauge(108, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_1 = gauge(109, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_2 = gauge(110, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_3 = gauge(111, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_4 = gauge(112, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_5 = gauge(113, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_6 = gauge(114, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_curve_y_7 = gauge(115, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_passive_cooling_supply_set_point = gauge(302, 0.01, nan=ABSENT_SENSOR, unit="°C")
    mix_valve_1_cooling_minimum_outdoor_temperature = gauge(303, 0.01, nan=ABSENT_SENSOR, unit="°C")

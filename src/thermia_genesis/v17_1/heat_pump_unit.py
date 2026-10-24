"""Heat pump unit (chapter 4)."""

from modbus_connection.model import enum, gauge, integer, uint32

from thermia_genesis.subsystem import (
    Subsystem,
    coil,
    discrete_input,
    holding_register,
    input_register,
)
from thermia_genesis.v17_1 import ABSENT_SENSOR
from thermia_genesis.v17_1.enums import ImmersionHeater, OutdoorTemperatureSource, SmartGridMode


class HeatPumpUnit(Subsystem):
    """The heat pump unit subsystem."""

    reset_all_alarms = coil(3)
    enable_external_additional_heater = coil(5)
    enable_flow_pressure_switch = coil(7)
    enable_tap_water = coil(8)
    enable_heat = coil(9)
    enable_brine_out_monitoring = coil(20)
    enable_brine_pump_continuous_operation = coil(21)
    enable_system_circulation_pump = coil(22)
    enable_additional_heater_only = coil(25)
    enable_variable_speed_condenser_pump = coil(34)
    enable_variable_speed_brine_pump = coil(35)
    enable_outdoor_temperature_dependent_external_heater = coil(39)
    enable_brine_in_monitoring = coil(40)
    enable_evaporator_freeze_protection = coil(42)
    enable_continuous_condenser_pump = coil(59)
    current_limiter_restricts_external_additional_heater = coil(60)
    current_limiter_restricts_secondary_units = coil(61)

    # Alarms
    alarm_class_a = discrete_input(0)
    alarm_class_b = discrete_input(1)
    alarm_class_c = discrete_input(2)
    alarm_class_d = discrete_input(3)
    high_pressure_switch_alarm = discrete_input(9)
    low_pressure_level_alarm = discrete_input(10)
    high_discharge_pipe_temperature_alarm = discrete_input(11)
    operating_pressure_limit_indication = discrete_input(12)
    discharge_pipe_sensor_alarm = discrete_input(13)
    liquid_line_sensor_alarm = discrete_input(14)
    suction_gas_sensor_alarm = discrete_input(15)
    flow_pressure_switch_alarm = discrete_input(16)
    power_input_phase_detection_alarm = discrete_input(22)
    inverter_unit_alarm = discrete_input(23)
    compressor_low_speed_alarm = discrete_input(25)
    low_super_heat_alarm = discrete_input(26)
    pressure_ratio_out_of_range_alarm = discrete_input(27)
    compressor_pressure_outside_envelope_alarm = discrete_input(28)
    brine_temperature_out_of_range_alarm = discrete_input(29)
    brine_in_sensor_alarm = discrete_input(30)
    brine_out_sensor_alarm = discrete_input(31)
    condenser_in_sensor_alarm = discrete_input(32)
    condenser_out_sensor_alarm = discrete_input(33)
    outdoor_sensor_alarm = discrete_input(34)
    brine_delta_out_of_range_alarm = discrete_input(49)
    brine_in_high_temperature_alarm = discrete_input(55)
    brine_in_low_temperature_alarm = discrete_input(56)
    brine_out_low_temperature_alarm = discrete_input(57)
    sum_alarm = discrete_input(66)
    inverter_unit_communication_alarm = discrete_input(75)
    secondary_unit_communication_alarm = discrete_input(83)
    other_primary_units_alarm = discrete_input(84)
    missing_secondary_units_alarm = discrete_input(85)
    tap_water_top_sensor_alarm = discrete_input(87)
    external_alarm_input = discrete_input(202)

    # Signals and states
    external_relay_brine_ground_water_pump = discrete_input(79)
    oil_boost_in_progress = discrete_input(86)
    compressor_control_signal = discrete_input(199)
    smart_grid_1_evu_input = discrete_input(201)
    smart_grid_2 = discrete_input(204)
    external_additional_heater_control_signal = discrete_input(206)
    condenser_pump_on = discrete_input(210)
    brine_pump_on = discrete_input(218)
    external_heater_circulation_pump_control_signal = discrete_input(219)
    external_additional_heater_active = discrete_input(221)
    stopping = discrete_input(224)
    ok_to_start = discrete_input(225)
    compressor_unable_to_speed_up = discrete_input(246)

    # Compressor
    compressor_available_gears = input_register(gauge(4, 0.01))
    compressor_speed = input_register(integer(5, signed=False, unit="rpm"))
    compressor_speed_percent = input_register(gauge(54, 0.01, unit="%"))
    compressor_start_restriction_timer = input_register(integer(60, signed=False))
    compressor_current_gear = input_register(gauge(61, 0.01))
    compressor_operating_hours = input_register(uint32(48, unit="h"))
    expansion_valve_opening_degree = input_register(gauge(315, 0.01, unit="%"))
    inverter_temperature = input_register(integer(319, unit="°C"))

    # Temperatures
    discharge_pipe_temperature = input_register(gauge(7, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    condenser_in_temperature = input_register(gauge(8, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    condenser_out_temperature = input_register(gauge(9, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    brine_in_temperature = input_register(gauge(10, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    brine_out_temperature = input_register(gauge(11, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    outdoor_temperature = input_register(gauge(13, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    room_temperature = input_register(gauge(121, 0.1, unit="°C"))
    liquid_line_temperature = input_register(gauge(129, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    suction_gas_temperature = input_register(gauge(130, 0.01, nan=ABSENT_SENSOR, unit="°C"))

    # Refrigerant circuit
    bubble_point_high_pressure_temperature = input_register(
        gauge(122, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    dew_point_high_pressure_temperature = input_register(
        gauge(123, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    dew_point_low_pressure_temperature = input_register(
        gauge(124, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    superheat_temperature = input_register(gauge(125, 0.01, unit="K"))
    sub_cooling_temperature = input_register(gauge(126, 0.01, unit="K"))
    low_pressure_side_pressure = input_register(gauge(127, 0.01, unit="bar(g)"))
    high_pressure_side_pressure = input_register(gauge(128, 0.01, unit="bar(g)"))

    # Pumps and additional heat
    condenser_circulation_pump_speed = input_register(gauge(39, 0.01, unit="%"))
    brine_circulation_pump_speed = input_register(gauge(44, 0.01, unit="%"))
    external_additional_heater_current_demand = input_register(gauge(6, 0.01, unit="%"))
    external_additional_heater_operating_hours = input_register(uint32(52, unit="h"))
    internal_immersion_heater_active_step = input_register(integer(67, signed=False))

    # Power, seasons and smart grid
    current_power_output = input_register(gauge(157, 0.01, unit="kW"))
    current_consumed_power = input_register(gauge(158, 0.01, unit="kW"))
    # Negative values have a meaning here, so these stay signed.
    cooling_season_integral_value = input_register(integer(36))
    heating_season_integral_value = input_register(integer(131))
    smart_grid_mode = input_register(enum(82, SmartGridMode))

    # Cascade: primary unit with Genesis secondaries
    available_secondaries = input_register(integer(143, signed=False))
    total_distributed_gears = input_register(integer(145, signed=False))
    maximum_requested_gear = input_register(integer(146, signed=False))
    # One bit per secondary heat pump unit.
    secondaries_class_d_alarm = input_register(integer(160, signed=False))
    secondaries_communication_alarm = input_register(integer(161, signed=False))
    secondaries_class_a_alarm = input_register(integer(162, signed=False))
    secondaries_class_b_alarm = input_register(integer(163, signed=False))

    # Control software version
    software_version_major = input_register(integer(311, signed=False))
    software_version_minor = input_register(integer(312, signed=False))
    software_version_micro = input_register(integer(313, signed=False))

    # Gears
    minimum_allowed_gear_in_heating = holding_register(integer(26, signed=False))
    maximum_allowed_gear_in_heating = holding_register(integer(27, signed=False))
    gear_shift_delay_heating = holding_register(integer(61, signed=False, unit="min"))

    # Brine limits
    brine_in_high_alarm_limit = holding_register(gauge(67, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    brine_in_low_alarm_limit = holding_register(gauge(68, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    brine_out_low_alarm_limit = holding_register(gauge(69, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    brine_max_delta_limit = holding_register(gauge(70, 0.01, unit="K"))

    # External additional heater
    # A PID sum, signed: the reference pump reads -6.
    external_additional_heater_start = holding_register(integer(75))
    external_additional_heater_stop = holding_register(gauge(78, 0.01))
    external_heater_outdoor_temperature_limit = holding_register(
        gauge(304, 0.01, nan=ABSENT_SENSOR, unit="°C")
    )
    enabled_immersion_heater = holding_register(enum(321, ImmersionHeater))

    # Pump speeds
    condenser_pump_lowest_allowed_speed = holding_register(gauge(76, 0.01, unit="%"))
    brine_pump_lowest_allowed_speed = holding_register(gauge(77, 0.01, unit="%"))
    condenser_pump_highest_allowed_speed = holding_register(gauge(79, 0.01, unit="%"))
    brine_pump_highest_allowed_speed = holding_register(gauge(80, 0.01, unit="%"))
    condenser_pump_standby_speed = holding_register(gauge(81, 0.01, unit="%"))
    brine_pump_standby_speed = holding_register(gauge(82, 0.01, unit="%"))

    # Outdoor temperature from a building management system (BMS)
    outdoor_temperature_source = holding_register(enum(117, OutdoorTemperatureSource))
    bms_outdoor_temperature = holding_register(gauge(118, 0.01, nan=ABSENT_SENSOR, unit="°C"))

    # Current and power limitation
    maximum_phase_current = holding_register(integer(119, signed=False, unit="A"))
    compressor_current_hysteresis = holding_register(integer(120, signed=False, unit="A"))
    # The meaning of each value depends on the mode (SG-Ready or PL/LU); see chapter 3.4.
    power_consumption_control_mode = holding_register(integer(124, signed=False))
    input_power_limit = holding_register(gauge(125, 0.1, unit="kW"))

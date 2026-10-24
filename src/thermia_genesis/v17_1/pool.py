"""Pool (chapter 8)."""

from modbus_connection.model import Component, coil, discrete_input, gauge, integer

from thermia_genesis.v17_1 import ABSENT_SENSOR


class PoolCoils(Component):
    """Coils of the pool."""

    enable_pool = coil(28)
    enable_external_additional_heater = coil(31)


class PoolDiscreteInputs(Component):
    """Discrete inputs of the pool."""

    return_line_sensor_alarm = discrete_input(76)
    external_stop = discrete_input(77)
    directional_valve_position = discrete_input(235)


class PoolInputRegisters(Component):
    """Input registers of the pool."""

    register_space = "input"

    # Listed only in chapter 8, not in chapter 3; see errata.md.
    supply_line_temperature = gauge(119, 0.01, nan=ABSENT_SENSOR, unit="°C")
    return_line_temperature = gauge(120, 0.01, nan=ABSENT_SENSOR, unit="°C")
    desired_gear = integer(142, signed=False)


class PoolHoldingRegisters(Component):
    """Holding registers of the pool."""

    register_space = "holding"

    # °C as in chapter 8, not % as in chapter 3: the reference pump reads 26.00; see errata.md.
    charge_set_point = gauge(58, 0.01, nan=ABSENT_SENSOR, unit="°C")
    return_temperature_to_heat_exchanger_set_point = gauge(299, 0.1, unit="°C")
    hysteresis_set_point = gauge(300, 0.1, unit="K")
    gear_shift_delay = integer(62, signed=False, unit="min")
    minimum_allowed_gear = integer(85, signed=False)
    maximum_allowed_gear = integer(86, signed=False)

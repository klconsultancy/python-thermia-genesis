"""Pool (chapter 8)."""

from modbus_connection.model import gauge, integer

from thermia_genesis.subsystem import (
    Subsystem,
    coil,
    discrete_input,
    holding_register,
    input_register,
)
from thermia_genesis.v17_1 import ABSENT_SENSOR, ABSENT_SENSOR_AT_SCALE_10


class Pool(Subsystem):
    """The pool subsystem."""

    enable_pool = coil(28)
    enable_external_additional_heater = coil(31)

    return_line_sensor_alarm = discrete_input(76)
    external_stop = discrete_input(77)
    directional_valve_position = discrete_input(235)

    # Listed only in chapter 8, not in chapter 3; see errata.md.
    supply_line_temperature = input_register(gauge(119, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    return_line_temperature = input_register(gauge(120, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    desired_gear = input_register(integer(142, signed=False))

    # °C as in chapter 8, not % as in chapter 3: the reference pump reads 26.00; see errata.md.
    charge_set_point = holding_register(gauge(58, 0.01, nan=ABSENT_SENSOR, unit="°C"))
    return_temperature_to_heat_exchanger_set_point = holding_register(
        gauge(299, 0.1, nan=ABSENT_SENSOR_AT_SCALE_10, unit="°C")
    )
    hysteresis_set_point = holding_register(gauge(300, 0.1, unit="K"))
    gear_shift_delay = holding_register(integer(62, signed=False, unit="s"))
    minimum_allowed_gear = holding_register(integer(85, signed=False))
    maximum_allowed_gear = holding_register(integer(86, signed=False))

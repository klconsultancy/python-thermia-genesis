"""Electric meter (chapter 9); requires the current limiter accessory."""

from modbus_connection.model import gauge, integer, uint32

from thermia_genesis.subsystem import Subsystem, coil, input_register


class ElectricMeter(Subsystem):
    """The electric meter subsystem."""

    # Also tells whether a meter is connected (docs/design.md).
    enable_current_limitation = coil(26)

    # Phase currents
    l1_current = input_register(gauge(69, 0.01, unit="A"))
    l2_current = input_register(gauge(70, 0.01, unit="A"))
    l3_current = input_register(gauge(71, 0.01, unit="A"))

    # Phase-to-neutral voltages
    l1_voltage = input_register(gauge(72, 0.01, unit="V"))
    l2_voltage = input_register(gauge(73, 0.01, unit="V"))
    l3_voltage = input_register(gauge(74, 0.01, unit="V"))

    # Phase-to-phase voltages
    l1_l2_voltage = input_register(gauge(75, 0.1, unit="V"))
    l2_l3_voltage = input_register(gauge(76, 0.1, unit="V"))
    l3_l1_voltage = input_register(gauge(77, 0.1, unit="V"))

    # Power and energy. A current limiter measures the house connection, so the phase power
    # may be negative when the house exports; see errata.md.
    l1_power = input_register(integer(78, unit="W"))
    l2_power = input_register(integer(79, unit="W"))
    l3_power = input_register(integer(80, unit="W"))
    meter_value = input_register(integer(81, signed=False, unit="kWh"))
    kwh_total = input_register(uint32(83, scale=0.1, word_order="little", unit="kWh"))

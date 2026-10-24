"""Electric meter (chapter 9); requires the current limiter accessory."""

from modbus_connection.model import Component, coil, gauge, integer, uint32


class ElectricMeterCoils(Component):
    """Coils of the electric meter."""

    # Also tells whether a meter is connected (docs/design.md).
    enable_current_limitation = coil(26)


class ElectricMeterInputRegisters(Component):
    """Input registers of the electric meter."""

    register_space = "input"

    # Phase currents
    l1_current = gauge(69, 0.01, unit="A")
    l2_current = gauge(70, 0.01, unit="A")
    l3_current = gauge(71, 0.01, unit="A")

    # Phase-to-neutral voltages
    l1_voltage = gauge(72, 0.01, unit="V")
    l2_voltage = gauge(73, 0.01, unit="V")
    l3_voltage = gauge(74, 0.01, unit="V")

    # Phase-to-phase voltages
    l1_l2_voltage = gauge(75, 0.1, unit="V")
    l2_l3_voltage = gauge(76, 0.1, unit="V")
    l3_l1_voltage = gauge(77, 0.1, unit="V")

    # Power and energy
    l1_power = integer(78, signed=False, unit="W")
    l2_power = integer(79, signed=False, unit="W")
    l3_power = integer(80, signed=False, unit="W")
    meter_value = integer(81, signed=False, unit="kWh")
    kwh_total = uint32(83, scale=0.1, word_order="little", unit="kWh")

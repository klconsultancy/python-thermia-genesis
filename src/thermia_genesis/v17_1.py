"""Register map for Genesis firmware 17.1 (chapter 3 of the protocol document)."""

from modbus_connection.model import Component, gauge, uint32


class InputRegisters(Component):
    """Read-only analog registers (chapter 3.3)."""

    register_space = "input"

    compressor_operating_hours = uint32(48, unit="h")
    electric_meter_kwh_total = uint32(83, scale=0.1, word_order="little", unit="kWh")


class HoldingRegisters(Component):
    """Read/write analog registers (chapter 3.4)."""

    register_space = "holding"

    brine_out_low_alarm_limit = gauge(69, 0.01, unit="°C")

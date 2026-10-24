"""Electric meter (chapter 9)."""

from modbus_connection.model import Component, uint32


class ElectricMeterInputRegisters(Component):
    """Input registers of the electric meter."""

    register_space = "input"

    kwh_total = uint32(83, scale=0.1, word_order="little", unit="kWh")

"""Heat (chapter 5)."""

from modbus_connection.model import Component, gauge

from thermia_genesis.v17_1 import ABSENT_SENSOR


class HeatInputRegisters(Component):
    """Input registers of the heating system."""

    register_space = "input"

    system_supply_line_temperature = gauge(12, 0.01, nan=ABSENT_SENSOR, unit="°C")

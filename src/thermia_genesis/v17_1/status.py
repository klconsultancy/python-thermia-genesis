"""Status: the operational mode and the demands (assigned in docs/design.md)."""

from modbus_connection.model import Component, enum, flags

from thermia_genesis.v17_1.enums import Demand, OperationalMode, RunningDemands


class StatusInputRegisters(Component):
    """Input registers of the status."""

    register_space = "input"

    # Currently running, by priority
    running_demand_1 = enum(1, Demand)
    running_demand_2 = enum(55, Demand)
    running_demand_3 = enum(56, Demand)
    running_demands = flags(2, RunningDemands)

    # Queued, by priority
    queued_demand_1 = enum(62, Demand)
    queued_demand_2 = enum(63, Demand)
    queued_demand_3 = enum(64, Demand)
    queued_demand_4 = enum(65, Demand)
    queued_demand_5 = enum(66, Demand)


class StatusHoldingRegisters(Component):
    """Holding registers of the status."""

    register_space = "holding"

    operational_mode = enum(0, OperationalMode)

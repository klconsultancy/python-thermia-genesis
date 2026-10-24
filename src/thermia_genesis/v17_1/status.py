"""Status: the operational mode and the demands (assigned in docs/design.md)."""

from modbus_connection.model import enum, flags

from thermia_genesis.subsystem import Subsystem, holding_register, input_register
from thermia_genesis.v17_1.enums import Demand, OperationalMode, RunningDemands


class Status(Subsystem):
    """The status subsystem."""

    # Currently running, by priority
    running_demand_1 = input_register(enum(1, Demand))
    running_demand_2 = input_register(enum(55, Demand))
    running_demand_3 = input_register(enum(56, Demand))
    running_demands = input_register(flags(2, RunningDemands))

    # Queued, by priority
    queued_demand_1 = input_register(enum(62, Demand))
    queued_demand_2 = input_register(enum(63, Demand))
    queued_demand_3 = input_register(enum(64, Demand))
    queued_demand_4 = input_register(enum(65, Demand))
    queued_demand_5 = input_register(enum(66, Demand))

    operational_mode = holding_register(enum(0, OperationalMode))

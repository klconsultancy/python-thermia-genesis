"""Energy statistics: what the display shows per 12 months; no protocol edition lists them.

The registers were decoded against the display of the reference pump (see errata.md).
"""

from typing import override

from modbus_connection.model import gauge
from modbus_connection.model.fields import RegisterField

from thermia_genesis.subsystem import Subsystem, input_register


class KwhMwhField(RegisterField[int]):
    """An energy in kWh over two registers: the kWh below 1000, then the whole MWh."""

    def __init__(self, address: int) -> None:
        """Declare the pair starting at ``address``, the kWh register."""
        super().__init__(address, count=2, unit="kWh")

    @override
    def decode(self, words: list[int], scale_exponent: int | None = None) -> int:
        kwh, mwh = words
        return mwh * 1000 + kwh


class EnergyStatistics(Subsystem):
    """The energy statistics subsystem.

    Each circuit has a block of 9 registers: auxiliary heater, consumed, delivered, COP and
    natural source. The display calls the periods months 1-12 and months 13-24, presumably
    the current 12 months and the 12 before; whether they roll per month or per calendar
    year is not verified yet (#33).
    """

    # Heating, months 1-12
    heating_aux_heater_months_1_to_12 = input_register(KwhMwhField(348))
    heating_consumed_months_1_to_12 = input_register(KwhMwhField(350))
    heating_delivered_months_1_to_12 = input_register(KwhMwhField(352))
    heating_cop_months_1_to_12 = input_register(gauge(354, 0.1))
    heating_natural_source_months_1_to_12 = input_register(KwhMwhField(355))

    # Tap water, months 1-12
    tap_water_aux_heater_months_1_to_12 = input_register(KwhMwhField(357))
    tap_water_consumed_months_1_to_12 = input_register(KwhMwhField(359))
    tap_water_delivered_months_1_to_12 = input_register(KwhMwhField(361))
    tap_water_cop_months_1_to_12 = input_register(gauge(363, 0.1))
    tap_water_natural_source_months_1_to_12 = input_register(KwhMwhField(364))

    # Heating, months 13-24
    heating_aux_heater_months_13_to_24 = input_register(KwhMwhField(380))
    heating_consumed_months_13_to_24 = input_register(KwhMwhField(382))
    heating_delivered_months_13_to_24 = input_register(KwhMwhField(384))
    heating_cop_months_13_to_24 = input_register(gauge(386, 0.1))
    heating_natural_source_months_13_to_24 = input_register(KwhMwhField(387))

    # Tap water, months 13-24
    tap_water_aux_heater_months_13_to_24 = input_register(KwhMwhField(389))
    tap_water_consumed_months_13_to_24 = input_register(KwhMwhField(391))
    tap_water_delivered_months_13_to_24 = input_register(KwhMwhField(393))
    tap_water_cop_months_13_to_24 = input_register(gauge(395, 0.1))
    tap_water_natural_source_months_13_to_24 = input_register(KwhMwhField(396))

from modbus_connection.mock import MockModbusUnit

from thermia_genesis.v17_1.electric_meter import ElectricMeterReadings
from thermia_genesis.v17_1.enums import ImmersionHeater, OutdoorTemperatureSource, SmartGridMode
from thermia_genesis.v17_1.heat import HeatReadings
from thermia_genesis.v17_1.heat_pump_unit import HeatPumpUnitReadings, HeatPumpUnitSettings


async def test_decodes_negative_scaled_value(mock_modbus_unit: MockModbusUnit) -> None:
    # Worked example from chapter 2.1: -5 °C at scale 100 is transmitted as 65036.
    mock_modbus_unit.holding[69] = 65036
    registers = HeatPumpUnitSettings(mock_modbus_unit)

    await registers.async_update()

    assert registers.brine_out_low_alarm_limit == -5.0


async def test_combines_msb_and_lsb_into_one_counter(mock_modbus_unit: MockModbusUnit) -> None:
    # Worked example from chapter 2.1: MSB 2 and LSB 2345 make 133417 hours.
    mock_modbus_unit.input[48] = [2, 2345]
    registers = HeatPumpUnitReadings(mock_modbus_unit)

    await registers.async_update()

    assert registers.compressor_operating_hours == 133417


async def test_combines_lsb_before_msb_into_scaled_counter(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    # The electric meter total lists its LSB (83) before its MSB (84), at scale 10.
    mock_modbus_unit.input[83] = [4, 1]
    registers = ElectricMeterReadings(mock_modbus_unit)

    await registers.async_update()

    assert registers.kwh_total == 6554.0


async def test_reads_absent_sensor_as_none(mock_modbus_unit: MockModbusUnit) -> None:
    # The reference pump reports 20000 (200.00 °C) for temperature sensors it doesn't have.
    mock_modbus_unit.input[12] = 20000
    registers = HeatReadings(mock_modbus_unit)

    await registers.async_update()

    assert registers.system_supply_line_temperature is None


async def test_reads_coil_as_bool(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.coil[9] = True
    settings = HeatPumpUnitSettings(mock_modbus_unit)

    await settings.async_update()

    assert settings.enable_heat is True


async def test_reads_discrete_input_as_bool(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.discrete[0] = True
    readings = HeatPumpUnitReadings(mock_modbus_unit)

    await readings.async_update()

    assert readings.alarm_class_a is True


async def test_reads_enum_from_footnote(mock_modbus_unit: MockModbusUnit) -> None:
    # Footnote *4: 1 EVU, 4 Normal, 5 Comfort, 6 Boost. The reference pump reads 4.
    mock_modbus_unit.input[82] = 4
    readings = HeatPumpUnitReadings(mock_modbus_unit)

    await readings.async_update()

    assert readings.smart_grid_mode is SmartGridMode.NORMAL


async def test_reads_enums_of_the_reference_pump(mock_modbus_unit: MockModbusUnit) -> None:
    # The reference pump uses its own outdoor sensor (chapter 3.4, register 117: 0) and has
    # the internal immersion heater enabled (footnote *7: 2).
    mock_modbus_unit.holding[117] = 0
    mock_modbus_unit.holding[321] = 2
    settings = HeatPumpUnitSettings(mock_modbus_unit)

    await settings.async_update()

    assert settings.outdoor_temperature_source is OutdoorTemperatureSource.PT1000_SENSOR
    assert settings.enabled_immersion_heater is ImmersionHeater.INTERNAL

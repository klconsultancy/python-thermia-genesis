from modbus_connection.mock import MockModbusUnit

from thermia_genesis import ThermiaGenesis
from thermia_genesis.v17_1.enums import (
    Demand,
    ImmersionHeater,
    MixValveMode,
    OperationalMode,
    OutdoorTemperatureSource,
    RunningDemands,
    SmartGridMode,
)


async def test_decodes_negative_scaled_value(mock_modbus_unit: MockModbusUnit) -> None:
    # Worked example from chapter 2.1: -5 °C at scale 100 is transmitted as 65036.
    mock_modbus_unit.holding[69] = 65036
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.brine_out_low_alarm_limit == -5.0


async def test_combines_msb_and_lsb_into_one_counter(mock_modbus_unit: MockModbusUnit) -> None:
    # Worked example from chapter 2.1: MSB 2 and LSB 2345 make 133417 hours.
    mock_modbus_unit.input[48] = [2, 2345]
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.compressor_operating_hours == 133417


async def test_combines_lsb_before_msb_into_scaled_counter(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    # The electric meter total lists its LSB (83) before its MSB (84), at scale 10.
    mock_modbus_unit.input[83] = [4, 1]
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.electric_meter.kwh_total == 6554.0


async def test_reads_absent_sensor_as_none(mock_modbus_unit: MockModbusUnit) -> None:
    # The reference pump reports 20000 (200.00 °C) for temperature sensors it doesn't have.
    mock_modbus_unit.input[12] = 20000
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat.system_supply_line_temperature is None


async def test_reads_coil_as_bool(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.coil[9] = True
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.enable_heat is True


async def test_reads_discrete_input_as_bool(mock_modbus_unit: MockModbusUnit) -> None:
    mock_modbus_unit.discrete[0] = True
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.alarm_class_a is True


async def test_reads_enum_from_footnote(mock_modbus_unit: MockModbusUnit) -> None:
    # Footnote *4: 1 EVU, 4 Normal, 5 Comfort, 6 Boost. The reference pump reads 4.
    mock_modbus_unit.input[82] = 4
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.smart_grid_mode is SmartGridMode.NORMAL


async def test_reads_enums_of_the_reference_pump(mock_modbus_unit: MockModbusUnit) -> None:
    # The reference pump uses its own outdoor sensor (chapter 3.4, register 117: 0) and has
    # the internal immersion heater enabled (footnote *7: 2).
    mock_modbus_unit.holding[117] = 0
    mock_modbus_unit.holding[321] = 2
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.outdoor_temperature_source is OutdoorTemperatureSource.PT1000_SENSOR
    assert pump.heat_pump.enabled_immersion_heater is ImmersionHeater.INTERNAL


async def test_reads_count_above_32767_as_positive(mock_modbus_unit: MockModbusUnit) -> None:
    # A timer can't be negative, so its register is unsigned.
    mock_modbus_unit.input[60] = 40000
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat_pump.compressor_start_restriction_timer == 40000


async def test_reads_mix_valve_mode(mock_modbus_unit: MockModbusUnit) -> None:
    # Chapter 3.4, register 298: 0 Heat, 1 Cool, 2 Auto.
    mock_modbus_unit.holding[298] = 2
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.heat.mix_valve_1_mode is MixValveMode.AUTO


async def test_reads_operational_mode(mock_modbus_unit: MockModbusUnit) -> None:
    # Footnote *2: 1 OFF, 2 Standby, 3 ON/Auto. The reference pump reads 3.
    mock_modbus_unit.holding[0] = 3
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.status.operational_mode is OperationalMode.ON_AUTO


async def test_reads_demand_and_running_demands(mock_modbus_unit: MockModbusUnit) -> None:
    # Footnote *1 gives 99 for no demand; footnote *6 gives bit 10 (1024) for it.
    # The reference pump reads 99 and 1024 while idle.
    mock_modbus_unit.input[1] = [99, 1024]
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.status.running_demand_1 is Demand.NO_DEMAND
    assert pump.status.running_demands == RunningDemands.NO_DEMAND


async def test_reads_several_running_demands_as_flags(mock_modbus_unit: MockModbusUnit) -> None:
    # Footnote *6: bit 2 hot water, bit 3 heat.
    mock_modbus_unit.input[2] = 0b1100
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.status.running_demands == RunningDemands.HOT_WATER | RunningDemands.HEAT


async def test_reads_negative_phase_power(mock_modbus_unit: MockModbusUnit) -> None:
    # A current limiter measures the house connection, so export can be negative.
    mock_modbus_unit.input[78] = 65036
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.electric_meter.l1_power == -500

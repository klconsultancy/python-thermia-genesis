from modbus_connection.mock import MockModbusUnit

from thermia_genesis.v17_1 import HoldingRegisters, InputRegisters


async def test_decodes_negative_scaled_value(mock_modbus_unit: MockModbusUnit) -> None:
    # Worked example from chapter 2.1: -5 °C at scale 100 is transmitted as 65036.
    mock_modbus_unit.holding[69] = 65036
    registers = HoldingRegisters(mock_modbus_unit)

    await registers.async_update()

    assert registers.brine_out_low_alarm_limit == -5.0


async def test_combines_msb_and_lsb_into_one_counter(mock_modbus_unit: MockModbusUnit) -> None:
    # Worked example from chapter 2.1: MSB 2 and LSB 2345 make 133417 hours.
    mock_modbus_unit.input[48] = [2, 2345]
    registers = InputRegisters(mock_modbus_unit)

    await registers.async_update()

    assert registers.compressor_operating_hours == 133417


async def test_combines_lsb_before_msb_into_scaled_counter(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    # The electric meter total lists its LSB (83) before its MSB (84), at scale 10.
    mock_modbus_unit.input[83] = [4, 1]
    registers = InputRegisters(mock_modbus_unit)

    await registers.async_update()

    assert registers.electric_meter_kwh_total == 6554.0

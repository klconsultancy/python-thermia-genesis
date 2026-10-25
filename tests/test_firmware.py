from typing import assert_type

from modbus_connection.exceptions import ServerDeviceFailureError
from modbus_connection.mock import MockModbusUnit

from thermia_genesis import FirmwareVersion, ThermiaGenesis


async def test_reads_the_firmware_version(mock_modbus_unit: MockModbusUnit) -> None:
    # The reference pump runs 17.1.11 (input 311-313: major, minor, micro).
    mock_modbus_unit.input[311] = [17, 1, 11]
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    version = pump.firmware_version
    assert_type(version, FirmwareVersion | None)
    assert version == FirmwareVersion(17, 1, 11)
    assert str(version) == "17.1.11"
    assert version.supported
    assert version >= (17, 1)


def test_has_no_firmware_version_before_the_first_update(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    pump = ThermiaGenesis(mock_modbus_unit)

    assert pump.firmware_version is None


async def test_reports_another_firmware_as_unsupported(mock_modbus_unit: MockModbusUnit) -> None:
    # The 17.1 map is still used; the caller decides how to warn.
    mock_modbus_unit.input[311] = [18, 0, 2]
    mock_modbus_unit.input[13] = 905
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    version = pump.firmware_version
    assert version == FirmwareVersion(18, 0, 2)
    assert not version.supported
    assert pump.heat_pump.outdoor_temperature == 9.05


async def test_has_no_firmware_version_when_the_first_read_fails(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    mock_modbus_unit.fail_read(311, ServerDeviceFailureError(), register_type="input")
    pump = ThermiaGenesis(mock_modbus_unit)

    await pump.async_update()

    assert pump.firmware_version is None


async def test_keeps_the_last_firmware_version_after_a_failed_read(
    mock_modbus_unit: MockModbusUnit,
) -> None:
    # Like every field: the report says the input registers failed, the value stays.
    mock_modbus_unit.input[311] = [17, 1, 11]
    pump = ThermiaGenesis(mock_modbus_unit)
    await pump.async_update()
    mock_modbus_unit.fail_read(311, ServerDeviceFailureError(), register_type="input")

    report = await pump.async_update()

    assert "input_registers" in report.failed
    assert pump.firmware_version == FirmwareVersion(17, 1, 11)

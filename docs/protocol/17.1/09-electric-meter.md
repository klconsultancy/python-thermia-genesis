# 9 Electric meter

## 9.1 Electric meter

For this function, the accessory "Current limiter" is required.

| Position number | Units  | Reference to | Address | De Facto Address | Scale | Description                        |
| --------------- | ------ | ------------ | ------- | ---------------- | ----- | ---------------------------------- |
|                 | on/off | 9            | 26      | 27               | 1     | Enable current limitation          |
|                 | A      | 9            | 69      | 30070            | 100   | Electric meter L1 current (A)      |
|                 | A      | 9            | 70      | 30071            | 100   | Electric meter L2 current (A)      |
|                 | A      | 9            | 71      | 30072            | 100   | Electric meter L3 current (A)      |
|                 | V      | 9            | 72      | 30073            | 100   | Electric meter L1-0 voltage (V)    |
|                 | V      | 9            | 73      | 30074            | 100   | Electric meter L2-0 voltage (V)    |
|                 | V      | 9            | 74      | 30075            | 100   | Electric meter L3-0 voltage (V)    |
|                 | V      | 9            | 75      | 30076            | 10    | Electric meter L1-L2 voltage (V)   |
|                 | V      | 9            | 76      | 30077            | 10    | Electric meter L2-L3 voltage (V)   |
|                 | V      | 9            | 77      | 30078            | 10    | Electric meter L3-L1 voltage (V)   |
|                 | W      | 9            | 78      | 30079            | 1     | Electric meter L1 power (W)        |
|                 | W      | 9            | 79      | 30080            | 1     | Electric meter L2 power (W)        |
|                 | W      | 9            | 80      | 30081            | 1     | Electric meter L3 power (W)        |
|                 | kWh    | 9            | 81      | 30082            | 1     | Electric meter - meter value (kWh) |
|                 |        | 9            | 83      | 30084            | 10    | Electric meter kWh total (LSB)     |
|                 |        | 9            | 84      | 30085            | 10    | Electric meter kWh total (MSB)     |

Footnotes:

\*1) 1: Manual operation, 2: Defrost, 3: Hot water, 4: Heat, 5: Active Cooling, 6: Pool, 7: Anti legionella, 8: Passive Cooling 98: Standby 99: No demand 100: OFF

\*2) 1: OFF, 2: Standby, 3: ON/Auto

\*3) Different heat pumps have different number of available gears.
For instance: Commercial can have 10, while domestic can have 9 gears.

\*4) These applies to Smart grid function. 1: EVU, 4: Normal, 5: Comfort, 6: Boost

\*5) Should always be set to 1 i auto mode

\*6) Bit 0: Manual operation Bit 1: Defrost, Bit 2: Hot water, Bit 3: Heat, Bit 4: Active Cooling, Bit 5: Pool, Bit 6: Anti legionella, Bit 7: Passive
Cooling, Bit 8: Reserved, Bit 9: Standby, Bit 10: No demand, Bit 11: OFF

\*7) 0=Disable immersion heater, 2=Internal immersion heater enabled

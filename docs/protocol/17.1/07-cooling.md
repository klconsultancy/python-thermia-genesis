# 7 Cooling

## 7.1 Cooling

| Position number | Units  | Reference to | Address | De Facto Address | Scal e | Description                               |
| --------------- | ------ | ------------ | ------- | ---------------- | ------ | ----------------------------------------- |
|                 | On/Off | 5            | 10      | 11               | 1      | Enable active cooling                     |
|                 | On/Off | 5            | 33      | 34               | 1      | Enable passive cooling (EM)               |
|                 |        | 5            | 63      | 40064            | 1      | Gear shift delay cooling                  |
|                 |        | 5            | 87      | 40088            | 1      | Minimum allowed gear in cooling \*3       |
|                 |        | 5            | 88      | 40089            | 1      | Maximum allowed gear in cooling \*3       |
| 345             | On/Off | 5            | 78      | 10079            | 1      | External start brine pump, read only (EM) |
|                 |        | 5            | 141     | 30142            | 1      | Desired gear for cooling                  |

## 7.2 Cooling circuit

| Position number | Units            | Reference to | Address | De Facto Address | Scale | Description                                                        |
| --------------- | ---------------- | ------------ | ------- | ---------------- | ----- | ------------------------------------------------------------------ |
| 58              | active/ inactive | 5            | 67      | 10068            | 1     | Cooling circuit supply line temperature deviation alarm (EM)       |
| 38              | on/off           | 5            | 236     | 10237            | 1     | Cooling circuit circulation pump control signal (EM)               |
|                 | on/off           | 5            | 240     | 10241            | 1     | Cooling circuit regulation control signal (EM)                     |
| 58              | °C               | 5            | 106     | 30107            | 100   | Cooling circuit supply line temperature (EM)                       |
| 74              | on/off           | 5            | 137     | 30138            | 1     | Mix valve cooling opening degree (EM2/3)                           |
| 74              | %                | 5            | 30      | 40031            | 100   | Cooling mix valve set point (EM)                                   |
| 74              | %                | 5            | 49      | 40050            | 100   | Cooling supply line mix valve: Lowest allowed opening degree (EM)  |
| 74              | %                | 5            | 50      | 40051            | 100   | Cooling supply line mix valve: Highest allowed opening degree (EM) |

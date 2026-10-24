# 8 Pool

## 8.1 Pool

| Position number | Units            | Reference to | Address | De Facto Address | Scale | Description                                            |
| --------------- | ---------------- | ------------ | ------- | ---------------- | ----- | ------------------------------------------------------ |
|                 | on/off           | 6            | 28      | 29               | 1     | Enable pool (EM)                                       |
|                 | on/off           | 6            | 31      | 32               | 1     | Enable external additional heater for pool (EM)        |
| 60              | active/ inactive | 6            | 76      | 10077            | 1     | Pool return line sensor alarm                          |
| 342             | on/off           | 6            | 77      | 10078            | 1     | External stop for pool, read only (EM)                 |
| 101             | on/off           | 6            | 235     | 10236            | 1     | Pool directional valve position (EM)                   |
| 183             | °C               | 6            | 119     | 30120            | 100   | Pool supply line temperature (EM)                      |
| 60              | °C               | 6            | 120     | 30121            | 100   | Pool return line temperature (EM)                      |
|                 |                  | 6            | 142     | 30143            | 1     | Desired gear for pool                                  |
| 183             | °C               | 6            | 58      | 40059            | 100   | Pool charge set point (EM)                             |
|                 |                  | 6            | 62      | 40063            | 1     | Gear shift delay pool                                  |
|                 |                  | 6            | 85      | 40086            | 1     | Minimum allowed gear in pool \*3                       |
|                 |                  | 6            | 86      | 40087            | 1     | Maximum allowed gear in pool \*3                       |
| 60              | °C               | 6            | 299     | 40300            | 10    | Set point return temp from pool to heat exchanger (EM) |
| 60              | K                | 6            | 300     | 40301            | 10    | Set point pool hysteresis (EM)                         |

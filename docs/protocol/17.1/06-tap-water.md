# 6 Tap water

## 6.1 Tap water

| Position number | Units            | Reference to | Address | De Facto Address | Scale | Description                                                                      |
| --------------- | ---------------- | ------------ | ------- | ---------------- | ----- | -------------------------------------------------------------------------------- |
| 34              | on/off           |              | 14      | 15               | 1     | Enable hot gas pump                                                              |
| 53              | active/ inactive | 2            | 50      | 10051            | 1     | Tap water mid sensor alarm                                                       |
| 55              | °C               | 2            | 15      | 30016            | 100   | Tap water top temperature                                                        |
| 53              | °C               | 2            | 16      | 30017            | 100   | Tap water lower temperature                                                      |
| 53/55           | °C               | 2            | 17      | 30018            | 100   | Tap water weighted temperature                                                   |
| 77              | %                | 2            | 47      | 30048            | 1     | Tap water valve position (%)                                                     |
|                 | h                | 2            | 50      | 30051            | 1     | Tap water operating hours (MSB)                                                  |
|                 | h                | 2            | 51      | 30052            | 1     | Tap water operating hours (LSB)                                                  |
|                 |                  | 2            | 139     | 30140            | 1     | Desired gear for tap water                                                       |
| 53/55           | °C               | 2            | 22      | 40023            | 100   | Start temperature tap water (only valid when tap water mode is Normal )          |
| 53/55           | °C               | 2            | 23      | 40024            | 100   | Stop temperature tap water (only valid when tap water mode is Normal )           |
|                 |                  | 2            | 28      | 40029            | 1     | Maximum allowed gear in tap water \*3 (only valid when tap water mode is Normal) |
|                 |                  | 2            | 29      | 40030            | 1     | Minimum allowed gear in tap water \*3 (only valid when tap water mode is Normal) |

## 6.2 HGW

| Position number | Units            | Reference to | Address | De Facto Address | Scale | Description                   |
| --------------- | ---------------- | ------------ | ------- | ---------------- | ----- | ----------------------------- |
| 364             | on/off           |              | 6       | 7                | 1     | Enable HGW                    |
| 364             | active/ inactive | 2            | 52      | 10053            | 1     | HGW sensor alarm              |
| 364             | on/off           | 2            | 223     | 10224            | 1     | HGW regulation control signal |
| 407             | °C               | 2            | 45      | 30046            | 100   | HGW supply line temperature   |
| 364             | %                | 2            | 47      | 30048            | 1     | HGW mix valve position (%)    |

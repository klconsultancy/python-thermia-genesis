# 5 Heat

## 5.1 Heating system

| Position number | Units            | Reference to | Address | De Facto Address | Scale | Description                                                              |
| --------------- | ---------------- | ------------ | ------- | ---------------- | ----- | ------------------------------------------------------------------------ |
|                 | on/off           |              | 41      | 42               | 1     | Enable fixed system supply set point, allows defacto address 40117       |
| 51              | active/ inactive | 1            | 24      | 10025            | 1     | System supply low temperature alarm                                      |
| 51              | active/ inactive | 1            | 35      | 10036            | 1     | System supply line sensor alarm                                          |
| 62              | active/ inactive |              | 74      | 10075            | 1     | Temperature room sensor alarm                                            |
| 36              | on/off           | 1            | 211     | 10212            | 1     | System circulation pump control signal                                   |
|                 |                  | 1            | 220     | 10221            | 1     | Heating season (winter) active                                           |
| 51              | °C               | 1            | 12      | 30013            | 100   | System supply line temperature (EM)                                      |
| 51              | °C               | 1            | 18      | 30019            | 100   | System supply line calculated set point                                  |
| 51              | °C               | 1            | 19      | 30020            | 100   | Selected heat curve, (system) supply line                                |
| 50              | °C               | 1            | 20      | 30021            | 100   | Heat curve, X-coordinate 1 (highest outdoor temperature)                 |
| 50              | °C               | 1            | 21      | 30022            | 100   | Heat curve, X-coordinate 2                                               |
| 50              | °C               | 1            | 22      | 30023            | 100   | Heat curve, X-coordinate 3                                               |
| 50              | °C               | 1            | 23      | 30024            | 100   | Heat curve, X-coordinate 4                                               |
| 50              | °C               | 1            | 24      | 30025            | 100   | Heat curve, X-coordinate 5                                               |
| 50              | °C               | 1            | 25      | 30026            | 100   | Heat curve, X-coordinate 6                                               |
| 50              | °C               | 1            | 26      | 30027            | 100   | Heat curve, X-coordinate 7 (lowest outdoor temperature)                  |
|                 | °C               |              | 27      | 30028            | 100   | System return line temperature.                                          |
|                 |                  | 10           | 30      | 30031            | 100   | Calculated demand (heat)                                                 |
|                 | °C               | 8            | 41      | 30042            | 100   | Buffer tank temperature (EM)                                             |
|                 | °C               | 8            | 68      | 30069            | 100   | Buffer tank charge set point                                             |
|                 |                  | 1            | 140     | 30141            | 1     | Desired gear for heating                                                 |
| 51              | °C               | 1            | 3       | 40004            | 100   | Max limitation, set point curve radiator                                 |
| 51              | °C               | 1            | 4       | 40005            | 100   | Min limitation, set point curve radiator                                 |
|                 | °C               | 1            | 5       | 40006            | 100   | Comfort wheel setting                                                    |
| 51              | °C               | 1            | 6       | 40007            | 100   | Set point heat curve, Y-coordinate 1 (highest outdoor temperature)       |
| 51              | °C               | 1            | 7       | 40008            | 100   | Set point heat curve, Y-coordinate 2                                     |
| 51              | °C               | 1            | 8       | 40009            | 100   | Set point heat curve, Y-coordinate 3                                     |
| 51              | °C               | 1            | 9       | 40010            | 100   | Set point heat curve, Y-coordinate 4                                     |
| 51              | °C               | 1            | 10      | 40011            | 100   | Set point heat curve, Y-coordinate 5                                     |
| 51              | °C               | 1            | 11      | 40012            | 100   | Set point heat curve, Y-coordinate 6                                     |
| 51              | °C               | 1            | 12      | 40013            | 100   | Set point heat curve, Y-coordinate 7 (lowest outdoor temperature)        |
|                 | °C               | 1            | 16      | 40017            | 100   | Heating season stop temperature                                          |
| 51              | °C               |              | 116     | 40117            | 100   | Fixed system supply set point, requires defacto address 42 to be enabled |

## 5.2 Mix valve 1

| Position number | Units            | Reference to | Address | De Facto Address | Scale | Description                                                                   |
| --------------- | ---------------- | ------------ | ------- | ---------------- | ----- | ----------------------------------------------------------------------------- |
| 107             | on/off           | 7            | 11      | 12               | 1     | Enable mix valve 1                                                            |
| 107             | on/off           | 5            | 37      | 38               | 1     | Enable outdoor temp dependent for cooling with mixing valve 1                 |
|                 | on/off           | 5            | 38      | 39               | 1     | Enable internal brine pump to start when cooling is active for mixing valve 1 |
| 108             | active/ inactive | 7            | 36      | 10037            | 1     | Mix valve 1 supply line sensor alarm                                          |
| 108             | active/ inactive | 7            | 60      | 10061            | 1     | Mix valve 1 supply temperature deviation alarm                                |
| 109             | on/off           | 7            | 209     | 10210            | 1     | Mix valve 1 circulation pump control signal (EM)                              |
| 107             | on/off           | 5            | 245     | 10246            | 1     | Indication when mixing valve 1 is producing passive cooling                   |
| 108             | °C               | 7            | 40      | 30041            | 100   | Mix valve 1 supply line temperature (EM)                                      |
| 107             | %                | 7            | 43      | 30044            | 100   | Mix valve 1 position (EM)                                                     |
| 108             | °C               | 7            | 147     | 30148            | 100   | Desired temperature distribution circuit Mix valve 1                          |
| 108             | °C               | 7            | 107     | 40108            | 100   | Min limitation Set point curve radiator Mix valve 1                           |
| 108             | °C               | 7            | 108     | 40109            | 100   | Max limitation Set point curve radiator Mix valve 1                           |
| 108             | °C               | 7            | 109     | 40110            | 100   | Set point curve, Y-coordinate 1 Mix valve 1 (highest outdoor temperature)     |
| 108             | °C               | 7            | 110     | 40111            | 100   | Set point curve, Y-coordinate 2 Mix valve 1                                   |
| 108             | °C               | 7            | 111     | 40112            | 100   | Set point curve, Y-coordinate 3 Mix valve 1                                   |
| 108             | °C               | 7            | 112     | 40113            | 100   | Set point curve, Y-coordinate 4 Mix valve 1                                   |
| 108             | °C               | 7            | 113     | 40114            | 100   | Set point curve, Y-coordinate 5 Mix valve 1                                   |
| 108             | °C               | 7            | 114     | 40115            | 100   | Set point curve, Y-coordinate 6 Mix valve 1                                   |
| 108             | °C               | 7            | 115     | 40116            | 100   | Set point curve, Y-coordinate 7 Mix valve 1 (lowest outdoor temperature)      |
| 108             | enum             |              | 298     | 40299            | 1     | Selected mode for mixing valve 1, 0:Heat, 1:Cool, 2:Auto                      |
| 108             | °C               | 5            | 302     | 40303            | 100   | Set point for supply line temp passive cooling with mixing valve 1            |
|                 | °C               | 5            | 303     | 40304            | 100   | Set point minimum outdoor temp when cooling is permitted                      |

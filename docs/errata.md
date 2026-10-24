# Errata

Contradictions and errors found in the Thermia Modbus protocol document 17.1, behaviour of
the reference pump that the document doesn't describe, and how the library handles each.
Chapter 3 (address list) wins unless the real register dump of the reference pump shows
otherwise.

## Register entries

| Register | Issue | Resolution |
| -------- | ----- | ---------- |
| Coil 25 "Enable additional heater only" | Scale 1 in chapter 3, scale 100 in chapter 4. | Scale 1 (chapter 3; coils are bits). |
| Holding register 61 "Gear shift delay heating" | Unit listed as `min`; the reference pump reads 300, which as minutes is a five-hour delay. | Unit kept as documented. To be verified: seconds seem more likely. |
| Holding register 30 "Cooling mix valve set point (EM)" | Unit listed as `%`; the reference pump reads 1800 (18.00), which equals the cooling start temperature (holding 105, 18.00 °C). | Unit kept as documented. To be verified: it may be a temperature. |
| Holding register 125 "Input power limit during Power Limitation" | The description calls itself "defacto 40125", but its de facto address is 40126; 40125 is register 124, whose own description refers to 40126 for the power limit. | Address 125 (the Address column). |
| Input register 137 "Mix valve cooling opening degree (EM2/3)" | Chapter 7 lists the unit as `on/off` for an opening degree; chapter 3 lists `%`. | `%` (chapter 3). |
| Coil 14 "Enable hot gas pump" and the HGW registers: coil 6 "Enable HGW", discrete 52 "HGW sensor alarm", discrete 223 "HGW regulation control signal", input 45 "HGW supply line temperature" | Listed only in chapter 6 (coil 14 in 6.1, the others in 6.2), not in chapter 3. The reference pump has no HGW: the coils and discrete inputs read `False`, input 45 reads 20000. | Mapped from chapter 6. |
| Input register 47 | Chapter 6 lists it twice: as "Tap water valve position (%)" (as in chapter 3) and as "HGW mix valve position (%)". The reference pump reads 0. | "Tap water valve position" (chapter 3). |
| Input registers 119–120 "Pool supply/return line temperature (EM)" | Listed in chapter 8 only, not in chapter 3 (holding 119–120 are different registers). The reference pump has no pool: both read 20000. | Mapped from chapter 8. |
| Holding register 58 "Pool charge set point (EM)" | Unit `°C` in chapter 8, `%` in chapter 3. | `%` (chapter 3). To be verified on a pump with a pool. |
| Input registers 83–84 "Electric meter kWh total" | LSB listed before MSB, the reverse of every other 32-bit pair. The reference pump has no electric meter (both read 0), so its dump cannot confirm the order. | LSB first, as documented. To be verified on a pump with an electric meter. |

## Document-wide

| Topic | Issue | Resolution |
| ----- | ----- | ---------- |
| Scale 100 (chapter 2.1) | The scale table says the transmitted value is "a tenfold larger"; the worked example in the same section transmits -5 °C as -500. | Hundredfold (the worked example; the reference pump's discharge pipe reads 2667: 26.67 °C, not 266.7 °C). |
| Footnotes | Printed at the end of chapter 9 instead of in their own chapter (as in 17.0). | Treated as document-wide footnotes. |

## Undocumented behaviour

Observed on the reference pump (firmware 17.1.11); the protocol document does not describe it.

| Registers | Behaviour | Handling |
| --------- | --------- | -------- |
| Temperature input registers (scale 100) | A sensor the pump doesn't have reads 20000 (200.00 °C), with no sensor alarm. The reference pump reads it on 12, 27, 40 and 41 (system supply, system return, mix valve 1 supply, buffer tank) while 106 (cooling supply, passive cooling enabled) reads 2224. | 20000 decodes as no value (`nan=ABSENT_SENSOR`). |
| Holding register 118 "Outdoor temperature sensor" | Reads 20000 (200.00 °C) when no BMS provides the outdoor temperature (register 117 is 0). | Decodes as no value (`nan=ABSENT_SENSOR`), like an absent sensor. |
| Addresses chapter 3 doesn't list | Every address up to at least 5000 answers in all four spaces: undocumented ones read 0 or `False` (input 28, 999 and 5000, holding 999 and 5000, coils and discrete inputs 999 and 5000), except input 14, which reads 1150. It sits between outdoor (13) and tap water top (15), so it may be a temperature at scale 100 (11.50 °C). Only far outside the map (65000) does the pump raise an illegal-address exception. | Missing subsystems are detected from their Enable coils, not from exceptions. |

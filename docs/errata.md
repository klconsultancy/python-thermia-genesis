# Errata

Contradictions and errors found in the Thermia Modbus protocol document 17.1, behaviour of
the reference pump that the document doesn't describe, and how the library handles each.
Chapter 3 (address list) wins unless the real register dump of the reference pump shows
otherwise.

## Register entries

| Register | Issue | Resolution |
| -------- | ----- | ---------- |
| Coil 25 "Enable additional heater only" | Scale 1 in chapter 3, scale 100 in chapter 4. | Scale 1 (chapter 3; coils are bits). |
| Input register 137 "Mix valve cooling opening degree (EM2/3)" | Unit listed as `on/off` for an opening degree. | To be verified against a register dump. |
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
| Addresses chapter 3 doesn't list | Every address up to at least 5000 answers in all four spaces: undocumented ones read 0 or `False` (input 28, 999 and 5000, holding 999 and 5000, coils and discrete inputs 999 and 5000), except input 14, which reads 1150. It sits between outdoor (13) and tap water top (15), so it may be a temperature at scale 100 (11.50 °C). Only far outside the map (65000) does the pump raise an illegal-address exception. | Missing subsystems are detected from their Enable coils, not from exceptions. |

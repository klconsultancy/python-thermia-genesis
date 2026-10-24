# Errata

Contradictions and errors found in the Thermia Modbus protocol document 17.1, and how the
library resolves them. Chapter 3 (address list) wins unless the real register dump of the
reference pump shows otherwise.

| Register | Issue | Resolution |
| -------- | ----- | ---------- |
| Scale 100 (chapter 2.1) | The scale table says the transmitted value is "a tenfold larger"; the worked example in the same section transmits -5 °C as -500. | Hundredfold (the worked example; the reference pump's discharge pipe reads 2667: 26.67 °C, not 266.7 °C). |
| Coil 25 "Enable additional heater only" | Scale 1 in chapter 3, scale 100 in chapter 4. | Scale 1 (chapter 3; coils are bits). |
| Input register 137 "Mix valve cooling opening degree (EM2/3)" | Unit listed as `on/off` for an opening degree. | To be verified against a register dump. |
| Input registers 83–84 "Electric meter kWh total" | LSB listed before MSB, the reverse of every other 32-bit pair. The reference pump has no electric meter (both read 0), so its dump cannot confirm the order. | LSB first, as documented. To be verified on a pump with an electric meter. |
| Temperature input registers (scale 100) | Not documented: a sensor the pump doesn't have reads 20000 (200.00 °C), with no sensor alarm. The reference pump reads it on 12, 27, 40 and 41 (system supply, system return, mix valve 1 supply, buffer tank) while 106 (cooling supply, passive cooling enabled) reads 2224. | 20000 decodes as no value (`nan=ABSENT_SENSOR`). |
| Footnotes | Printed at the end of chapter 9 instead of in their own chapter (as in 17.0). | Treated as document-wide footnotes. |

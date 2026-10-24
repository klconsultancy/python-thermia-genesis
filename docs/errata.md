# Errata

Contradictions and errors found in the Thermia Modbus protocol document 17.1, and how the
library resolves them. Chapter 3 (address list) wins unless the real register dump of the
reference pump shows otherwise.

| Register | Issue | Resolution |
| -------- | ----- | ---------- |
| Coil 25 "Enable additional heater only" | Scale 1 in chapter 3, scale 100 in chapter 4. | Scale 1 (chapter 3; coils are bits). |
| Input register 137 "Mix valve cooling opening degree (EM2/3)" | Unit listed as `on/off` for an opening degree. | To be verified against a register dump. |
| Input registers 83–84 "Electric meter kWh total" | LSB listed before MSB, the reverse of every other 32-bit pair. The reference pump has no electric meter (both read 0), so its dump cannot confirm the order. | LSB first, as documented. To be verified on a pump with an electric meter. |
| Footnotes | Printed at the end of chapter 9 instead of in their own chapter (as in 17.0). | Treated as document-wide footnotes. |

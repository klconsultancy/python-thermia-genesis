# Context

Domain terms used in code, docs and issues.

**Genesis**
: Thermia's controller platform. Its firmware version (e.g. 17.1.11) decides which Modbus
register map applies.

**Register space**
: One of the four Modbus data tables: *coils* (read/write bits), *discrete inputs* (read-only
bits), *input registers* (read-only 16-bit words) and *holding registers* (read/write 16-bit
words).

**Address / de facto address**
: The protocol document lists both. *Address* is the zero-based offset used on the wire.
The *de facto address* adds a prefix per register space (coils 1, discrete inputs 10001,
input registers 30001, holding registers 40001). The library uses the zero-based address.

**Scale**
: The factor the transmitted value is larger than the real value (1, 10 or 100).

**MSB / LSB**
: The high and low 16-bit halves of a 32-bit counter, stored in two registers.

**Absent sensor**
: A temperature sensor the installation doesn't have. Its input register reads 20000
(200.00 °C) instead of raising a sensor alarm; the library decodes it as no value (`None`).

**Subsystem**
: A functional part of the installation, matching chapters 4–9 of the protocol document:
heat pump unit, heat, tap water, cooling, pool and electric meter.

**EM (extension module)**
: Optional hardware (EM, EM2, EM3) that adds circuits such as passive cooling. Registers
marked "(EM)" only exist with an extension module.

**Gear**
: The compressor speed step of an inverter heat pump.

**Operational mode**
: The user-selected mode of the pump: off, standby or on/auto.

**Smart grid mode**
: The external energy-tariff mode: EVU, normal, comfort or boost.

**Primary / secondary unit**
: In cascaded installations one primary controller drives secondary heat pump units.

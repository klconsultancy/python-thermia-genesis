"""Register map for Genesis firmware 17.1, one module per subsystem (chapters 4-9)."""

# Temperature sensors the pump doesn't have read 20000 (200.00 °C); see errata.md.
ABSENT_SENSOR = 20000
# The same 200.0 °C for a temperature at scale 10, such as the room sensor (input 121).
ABSENT_SENSOR_AT_SCALE_10 = 2000

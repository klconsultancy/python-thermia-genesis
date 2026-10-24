"""Register map for Genesis firmware 17.1, one module per subsystem (chapters 4-9)."""

# Temperature sensors the pump doesn't have read 20000 (200.00 °C); see errata.md.
ABSENT_SENSOR = 20000

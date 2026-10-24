# Design

The current design of `thermia-genesis` and the reasons behind it. This is a living
document: when a choice changes, edit the relevant section. Git keeps the history.

Domain terms are defined in [`CONTEXT.md`](../CONTEXT.md).

## Scope

- Thermia heat pumps on the **Genesis** platform (Atlas, Calibra, Calibra E, Calibra Cool,
  Calibra RXT, Diplomat Inverter), controlled over **Modbus**.
- Only firmware **17.1** is implemented. The register map lives in a per-version module
  (`v17_1`) so other versions can be added side by side later.
- Reference hardware: Calibra 7, firmware 17.1.11, Modbus TCP, EM3 extension module with
  passive cooling.
- Modbus TCP first. RTU is not excluded: `modbus-connection` already supports serial and
  RTU-over-TCP, so adding it is mostly config-flow work in the integration.
- Read-only first. A write API is designed and tested in the library, but the Home
  Assistant integration does not expose it until a later milestone.

## Connection

- Built on [`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/)
  with the `tmodbus` backend, the same stack Home Assistant core uses.
- The library never owns a connection. Every API takes a `ModbusUnit`; the caller (Home
  Assistant's `modbus` integration, a script, a test) creates and closes the connection.
- On Modbus TCP the Genesis controller ignores the unit id; we use unit id 1.

## Register map

- **Source of truth:** chapter 3 (address list) of the Thermia Modbus protocol document,
  transcribed in [`docs/protocol/17.1`](protocol/17.1/). It decides address, register space,
  scale and unit. Chapters 4–9 are only used to group registers per subsystem. Enum and
  bit-flag values come from the footnotes.
- Registers are **hand-written** with `modbus_connection.model` field types (`gauge`,
  `integer(signed=True)`, `coil`, `discrete_input`, `enum`, ...). No CSV or code generator:
  the map is small enough that readable, reviewable code wins.
- The `v17_1` package has one module per subsystem (`heat_pump_unit`, `heat`, `tap_water`,
  `cooling`, `pool`, `electric_meter`, `status`). Each module has one component per Modbus
  register space it uses, named after it: `HeatPumpUnitCoils`, `HeatPumpUnitDiscreteInputs`,
  `HeatPumpUnitInputRegisters`, `HeatPumpUnitHoldingRegisters`. This mirrors the tables of
  chapter 3. Enums from the footnotes live in `v17_1.enums`.
- The map is read-only for now: no field is declared writable. Writing coils and holding
  registers comes with the write API (#19, see Scope).
- Chapters 4–9 list a few registers that chapter 3 doesn't (HGW, pool temperatures). They
  are mapped from their chapter and recorded in the errata.
- A register belongs to the subsystem of the chapter (4–9) that lists it. Chapters 4–9 leave
  some registers out or group them oddly, so these are assigned explicitly:
  - cooling: holding 105 and 106 (start/stop temperature), discrete 47, 238 and 242;
  - status: operational mode (holding 0) and every demand (input 1, 2, 55, 56, 62–66), even
    though chapter 4 lists 55, 56 and 62–66 under the heat pump unit;
  - heat pump unit: the cascade registers (input 143, 145, 146, 160–163), coil 40 and the
    power limitation (holding 124 and 125).
- A **consistency test** parses the markdown tables and checks that every register in the
  map is documented in the same register space with the same scale, sits in the module of
  its subsystem, and that each half of a 32-bit value sits on the register the document
  labels MSB or LSB. For every subsystem that is complete, it also checks the reverse: each
  of its documented registers is in the map. Once all subsystems are complete, this covers
  the whole of chapter 3. It also enforces the encoding rules below (absent sensor,
  signedness), and checks every row of chapters 4–9 against chapter 3; the rows that differ
  are listed with their errata entry.
- Contradictions in the documentation, behaviour of the reference pump the documentation
  doesn't describe, and how we handle each, are recorded in [`errata.md`](errata.md). The
  real register dump of the reference pump decides.

## Encoding

- Signed values use two's complement in a single 16-bit register. The document doesn't say
  which registers are signed, so the map decides per field type:
  - scaled values (`gauge`) are signed. Temperatures and set points go below zero, and a
    scaled raw value never reaches 32768 in practice, so the sign costs nothing;
  - unscaled numbers (`integer`) are unsigned, so a count, timer or meter value above 32767
    doesn't turn negative. The exceptions are values that can be negative: the season
    integrals and the PID sum of the external heater (the reference pump reads -150 and -6),
    and unscaled temperatures. The consistency test lists them, each with its reason;
  - enums, bit fields and 32-bit counters are unsigned.
- Scales are 1, 10 or 100 (the transmitted value is that many times larger). The map
  declares the inverse multiplier `modbus_connection` expects (`gauge(69, 0.01)` for 100).
- 32-bit counters are split in an MSB and an LSB register and combined as
  `MSB × 65536 + LSB`, declared with `uint32`. The order differs per register: the operating
  hours put the MSB first (`word_order="big"`), the electric meter kWh total puts the LSB
  first (`word_order="little"`).
- A temperature sensor the pump doesn't have reads 20000 (200.00 °C). Every °C register at
  scale 100 declares `nan=ABSENT_SENSOR`, so the value is `None` instead of a bogus reading.
  That includes holding registers: the BMS outdoor temperature (holding 118) reads 20000 when
  no BMS provides it.
- Decoding itself is `modbus_connection`'s; our tests check it per field type through the
  components, using the worked examples of chapter 2.1.

## Public API

Grouped per subsystem, following the domain rather than the Modbus register spaces:

```python
pump = ThermiaGenesis(unit)
report = await pump.async_update()
pump.heat_pump.compressor_operating_hours
pump.heat.system_supply_temperature
pump.cooling.supply_line_temperature
pump.status.operational_mode
pump.firmware_version
```

Internally the reads are planned per register space and pooled into as few block reads as
possible. `async_update()` returns an `UpdateReport` so callers can tell which parts failed.

## Firmware and subsystem detection

- The firmware version is read from input registers 311–313 (major, minor, micro).
- On a major/minor version other than 17.1 the library still uses the 17.1 map; the Home
  Assistant integration raises a repair issue.
- Optional subsystems are detected from their "Enable ..." coils: passive cooling (EM)
  coil 33, active cooling coil 10, pool (EM) coil 28, mix valve 1 coil 11, and the electric
  meter coil 26 ("Enable current limitation"; chapter 9 requires the current limiter).
- The pump answers every address up to at least 5000 in all four register spaces, so a
  missing subsystem never shows up as an illegal-address exception. Values of a sensor the
  pump doesn't have decode as `None` (see Encoding).
- There is no register for the model or a serial number.

## Tooling and process

- Python ≥ 3.12, tested on 3.12, 3.13 and 3.14.
- uv (with a committed `uv.lock`), hatchling, ruff (`ALL` rules), mypy strict, prek.
- Strict TDD: red, green, refactor. CI enforces 100% line and branch coverage.
- Every change goes through a pull request with a Conventional Commits title. release-please
  turns merged commits into a release PR; merging it tags `vX.Y.Z`, creates a GitHub
  Release and publishes to PyPI via trusted publishing, after a manual approval on the
  `pypi` environment. There is no TestPyPI step: CI runs `twine check --strict` on every
  build, and a bad release can be yanked and replaced by a patch release.
- Development happens in the devcontainer; nothing has to be installed on the host.
- Every change is made in a git worktree under `.worktrees/<branch>`, never in the main
  checkout. Worktrees use relative paths (`worktree.useRelativePaths`) so they also work
  inside the devcontainer, and each worktree has its own `.venv`.

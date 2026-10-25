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
- Read-only first. A write API will be designed and tested in the library (#19), but the
  Home Assistant integration does not expose it until a later milestone.

## Connection

- Built on [`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/)
  with the `tmodbus` backend, the same stack Home Assistant core uses.
- Home Assistant's `modbus` integration pins an exact `modbus-connection` version per
  release, and the integration installs the library next to it. So the library requires a
  wide range (`>=4.12.3,<5`, the version of Home Assistant 2026.10.0), and CI also runs the
  tests on that lower bound. Raise it only when the library needs a newer feature.
- The library never owns a connection. Every API takes a `ModbusUnit`; the caller (Home
  Assistant's `modbus` integration, a script, a test) creates and closes the connection.
- On Modbus TCP the Genesis controller ignores the unit id; we use unit id 1.

## Register map

- **Source of truth:** chapter 3 (address list) of the Thermia Modbus protocol document,
  transcribed in [`docs/protocol/17.1`](protocol/17.1/). It decides address, register space,
  scale and unit, unless [`errata.md`](errata.md) records otherwise (for example the unit of
  holding 58). Chapters 4–9 are only used to group registers per subsystem. Enum and
  bit-flag values come from the footnotes.
- Registers are **hand-written** with `modbus_connection.model` field types (`gauge`,
  `integer`, `coil`, `discrete_input`, `enum`, ...). No CSV or code generator:
  the map is small enough that readable, reviewable code wins.
- The `v17_1` package has one module per subsystem (`heat_pump_unit`, `heat`, `tap_water`,
  `cooling`, `pool`, `electric_meter`, `status`), each with one `Subsystem` class
  (`HeatPumpUnit`, `Heat`, ...). It declares every field once, wrapped in its register space:
  `coil(11)`, `discrete_input(220)`, `input_register(gauge(12, ...))`,
  `holding_register(gauge(5, ...))`. Enums from the footnotes live in `v17_1.enums`.
- `thermia_genesis.subsystem` builds one `modbus_connection` component per register space
  from those declarations (`HeatCoils`, `HeatDiscreteInputs`, `HeatInputRegisters`,
  `HeatHoldingRegisters`), so a component holds one space, as `modbus_connection` requires.
  Each declared field is a typed descriptor that reads its value from that component.
  Assigning to a field raises `AttributeError` (and mypy rejects it) until the write API
  (#19). A subclass keeps the fields it inherits, so a later firmware can extend a
  subsystem of 17.1 instead of copying it.
- Field names follow the document's description, without the name of their own subsystem
  as prefix: the class already says it (`pump.tap_water.top_temperature`, not
  `tap_water_top_temperature`; `pump.mix_valve_1.position`). A register named after another
  subsystem keeps that name (`tap_water_top_sensor_alarm` in the heat pump unit).
- The optional parts mix valve 1 (chapter 5.2) and HGW (chapter 6.2) are subsystems of their
  own (`MixValve1` in `heat`, `Hgw` in `tap_water`), so they can be left out like the other
  optional subsystems.
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
  labels MSB or LSB. It also checks the reverse: every documented register belongs to a
  subsystem and is in the map, so the map covers the whole of chapter 3 plus the registers
  only chapters 4–9 list (266 registers in 262 fields). It also enforces the encoding rules
  below (absent sensor, signedness), and checks every row of chapters 4–9 against chapter 3;
  the rows that differ are listed with their errata entry.
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
    the electric meter's phase power (export at the house connection) and unscaled
    temperatures. The consistency test lists them, each with its reason;
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
  no BMS provides it. At scale 10 the same 200.0 °C is 2000, so every °C register at scale 10
  (the room temperature, input 121, and holding 299) declares `nan=ABSENT_SENSOR_AT_SCALE_10`.
- Decoding itself is `modbus_connection`'s; our tests check it per field type through the
  components, using the worked examples of chapter 2.1.

## Public API

Grouped per subsystem, following the domain rather than the Modbus register spaces:

```python
pump = ThermiaGenesis(unit)
report = await pump.async_update()
pump.heat_pump.compressor_operating_hours
pump.heat.system_supply_line_temperature
pump.cooling.circuit_supply_line_temperature
pump.status.operational_mode
```

- `ThermiaGenesis` is a `modbus_connection` `Device`. Its subsystems are `heat_pump`,
  `heat`, `tap_water` and `status`, and the optional `mix_valve_1`, `hgw`, `cooling`, `pool`
  and `electric_meter` (see below). A caller asks the
  subsystem for a value and never sees the register space it comes from. Every field is
  typed (`pump.heat.system_supply_line_temperature` is `float | None` for mypy); a test
  checks that with `assert_type`.
- `async_update()` reads with one `ComponentGroup` per register space, so adjacent registers
  share a read, also across subsystems. A read never bridges a gap (`max_gap = 0`): it
  touches only mapped addresses. The reference pump answers any address, but another model
  or firmware may refuse one the document doesn't list. The whole map takes 68 block reads,
  about 0.4 s on the reference pump (bridging the gaps would take 9 reads and 0.1 s).
- `ThermiaGenesis(unit, max_block_size=...)` caps the addresses one read asks for (2–125,
  default 125; 2 is the widest field of the map, a 32-bit counter). An older Diplomat Inverter's Modbus interface failed on reads of 16
  registers (CJNE/thermiagenesis#236), so such a pump needs a lower value. A pause between
  requests belongs to the connection (`message_spacing` in `modbus_connection`).
- `async_update()` returns the `UpdateReport` of `Device.async_poll`, with one entry per
  register space (`coils`, `discrete_inputs`, `input_registers`, `holding_registers`): a
  failed read stops only its own space. Like `async_poll`, it raises `ModbusConnectionError`
  when the link is down, and `ModbusTimeoutError` when nothing has answered yet.
- A register the pump refuses (illegal address or function) doesn't take its space down. On
  such a refusal the library reads each field of that space on its own, once, leaves out the
  fields the pump refuses (`restrict_fields`: they read `None`, with a warning naming the
  register and the field, or one warning if the pump refuses the whole space), and reads the
  space again in the same update. Any other error still fails the space; one during that
  search fails only the space too, and the next update searches again. Only a lost
  connection raises. One refused register made ~400 entities unavailable in another
  integration (CJNE/pythermiagenesis#8). The dump command keeps reporting a refusal under
  `failed`, since a bug report needs to show it.

## Dump CLI

- `thermia-genesis dump <target>` (`thermia_genesis.cli`) takes the connection arguments of
  `modbus_connection.cli_helper` (TCP or serial) and `--unit` (default 1).
- It reads what `ThermiaGenesis` reads, so only mapped addresses of the parts the pump has.
  It writes one JSON object: `firmware`, `parts` (which optional parts are present),
  `registers` (raw values per register space, for test fixtures), `values` (decoded per
  subsystem; an enum as its name, a flag as the names of its members) and `failed`. It never
  writes to the pump.
- `registers` always holds the six Enable coils, also of absent parts, so a fixture answers
  them as the pump does (`False`, not a refusal).
- The register spaces are read one by one. A space whose read fails is left out and listed
  under `failed` by the same space name as in `registers`; the JSON is still written and the
  exit status is 1. A lost connection or a timeout ends the command with status 1 and no JSON.
- `--max-block-size` passes `max_block_size` on, so a pump that fails on long reads can be
  dumped too.
- Only mapped addresses are read. An undocumented address, such as input 14 in the errata,
  is checked with a separate read.

## Firmware and subsystem detection

- The firmware version is read from input registers 311–313 (major, minor, micro), with
  every update. `pump.firmware_version` is a `FirmwareVersion` named tuple (`str()` gives
  "17.1.11", it compares as a tuple), or `None` until an update has read it.
- On a major/minor version other than 17.1 the library still uses the 17.1 map;
  `FirmwareVersion.supported` is then `False`, and the caller decides how to warn (the Home
  Assistant integration raises a repair issue).
- Optional subsystems are detected from their "Enable ..." coils: mix valve 1 coil 11, HGW
  coil 6, cooling coil 10 (active) or coil 33 (passive, EM), pool (EM) coil 28, and the
  electric meter coil 26 ("Enable current limitation"; chapter 9 requires the current
  limiter).
- The first `async_update()` reads those six coils (the setup of `Device`) and creates only
  the parts that are enabled. A part the pump doesn't have stays `None`, typed as for example
  `Pool | None`, so mypy makes a caller handle it, and its registers are never read. The
  detection runs once: a part enabled later appears after the integration reloads.
- Each Enable coil is read on its own with `read_optional`. A coil the pump refuses (illegal
  address or function; coil 6 is listed only in chapter 6) leaves out only its part, with a
  log line. A lost connection or a timeout propagates, and the next update detects again.
- The pump answers every address up to at least 5000 in all four register spaces, so a
  missing subsystem never shows up as an illegal-address exception. Values of a sensor the
  pump doesn't have decode as `None` (see Encoding).
- There is no register for the model or a serial number.

## Tooling and process

- Tests use `modbus_connection`'s mock unit, and end-to-end tests run the library over real
  Modbus TCP against an in-process `tmodbus` server that replays a captured fixture
  (`tests/fixtures/`) and refuses every address the fixture doesn't hold.
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

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
- A **consistency test** parses the markdown tables and checks that every documented
  register exists in the map with the same address and scale.
- Contradictions in the documentation, and how we resolved them, are recorded in
  [`errata.md`](errata.md). The real register dump of the reference pump decides.

## Encoding

- Signed values use two's complement in a single 16-bit register.
- Scales are 1, 10 or 100 (the transmitted value is that many times larger).
- 32-bit counters are split in an MSB and an LSB register and combined as
  `MSB × 65536 + LSB`.

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
- Optional subsystems (EM cooling, active cooling, pool, mix valve 1, electric meter) are
  detected from their "Enable ..." coils. Registers the pump refuses with an illegal-address
  exception are treated as optional.
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

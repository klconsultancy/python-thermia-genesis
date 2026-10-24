# thermia-genesis

[![CI](https://github.com/klconsultancy/python-thermia-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/klconsultancy/python-thermia-genesis/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/thermia-genesis)](https://pypi.org/project/thermia-genesis/)
[![Python versions](https://img.shields.io/pypi/pyversions/thermia-genesis)](https://pypi.org/project/thermia-genesis/)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/klconsultancy/python-thermia-genesis/badge)](https://scorecard.dev/viewer/?uri=github.com/klconsultancy/python-thermia-genesis)
[![License: MIT](https://img.shields.io/github/license/klconsultancy/python-thermia-genesis)](LICENSE)
[![Coverage: 100%](https://img.shields.io/badge/coverage-100%25-brightgreen)](pyproject.toml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://img.shields.io/badge/mypy-strict-blue)](https://mypy-lang.org/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

Async Python library for Thermia heat pumps on the **Genesis** platform (Atlas, Calibra,
Calibra E, Calibra Cool, Calibra RXT, Diplomat Inverter), using Modbus via
[`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/).

> **Status:** early development. Only Genesis firmware 17.1 is targeted.

This library powers the [Thermia Genesis Home Assistant integration](https://github.com/klconsultancy/ha-thermia-genesis).

## Installation

```sh
pip install "thermia-genesis[tmodbus]"
```

## Usage

```python
import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from thermia_genesis import ThermiaGenesis


async def main() -> None:
    connection = ModbusConnection(ModbusTcpParams(host="192.0.2.10"), timeout=5)
    await connection.connect()
    try:
        # On Modbus TCP the Genesis controller ignores the unit id.
        pump = ThermiaGenesis(connection.for_unit(1))
        report = await pump.async_update()
        print(report.complete, pump.heat_pump.outdoor_temperature)
    finally:
        await connection.close()


asyncio.run(main())
```

The library only reads; it never writes to the pump.

## Development

Changes are made in git worktrees under `.worktrees/`, and the tools run in the
repository's devcontainer:

```sh
git config worktree.useRelativePaths true
git worktree add .worktrees/my-change -b my-change origin/main
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . uv run --directory .worktrees/my-change pytest
```

See [`AGENTS.md`](AGENTS.md) for the workflow and [`docs/design.md`](docs/design.md) for the
design.

## Disclaimer

Not affiliated with Thermia AB. Controlling a heat pump remotely is at your own risk.

## License

MIT

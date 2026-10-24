# thermia-genesis

[![CI](https://github.com/klconsultancy/python-thermia-genesis/actions/workflows/ci.yml/badge.svg)](https://github.com/klconsultancy/python-thermia-genesis/actions/workflows/ci.yml)

Async Python library for Thermia heat pumps on the **Genesis** platform (Atlas, Calibra,
Calibra E, Calibra Cool, Calibra RXT, Diplomat Inverter), using Modbus via
[`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/).

> **Status:** early development. Only Genesis firmware 17.1 is targeted.

This library powers the [Thermia Genesis Home Assistant integration](https://github.com/klconsultancy/ha-thermia-genesis).

## Installation

```sh
pip install "thermia-genesis[tmodbus]"
```

## Development

Open the repository in its devcontainer, then:

```sh
uv run pytest
```

See [`AGENTS.md`](AGENTS.md) for the workflow and [`docs/design.md`](docs/design.md) for the
design.

## Disclaimer

Not affiliated with Thermia AB. Controlling a heat pump remotely is at your own risk.

## License

MIT

# Agent instructions

Async Python library for Thermia heat pumps on the Genesis platform via Modbus. Read
[`docs/design.md`](docs/design.md) for the design and [`CONTEXT.md`](CONTEXT.md) for domain
terms before changing code.

## Workflow

- **Strict TDD.** Write one failing test, run it and confirm it fails for the right reason,
  then write the minimum code to pass, then refactor. Never write production code without a
  failing test that requires it.
- Coverage must stay at 100% (line and branch); CI fails otherwise.
- Work on a branch and open a pull request. Never push to `main`.
- PR titles and squash commits follow Conventional Commits (`feat:`, `fix:`, `docs:`,
  `test:`, `refactor:`, `build:`, `ci:`, `chore:`). They drive release-please.
- When a design choice or domain term changes, update `docs/design.md` or `CONTEXT.md` in
  the same PR. Do not create ADRs.

## Commands

Run inside the devcontainer:

```sh
uv run pytest          # tests + coverage gate
uv run ruff format     # format
uv run ruff check      # lint
uv run mypy            # type-check (strict)
uv run prek run -a     # all pre-commit hooks
```

## Registers

- Chapter 3 of `docs/protocol/17.1/03-address-list.md` is the source of truth. Use the
  zero-based *Address* column, not the de facto address.
- Record any contradiction in the documentation in `docs/errata.md`.
- Never write to a real heat pump from tests. Tests use `modbus_connection`'s mock unit or
  an in-process `tmodbus` server.

# Contributing

Thanks for your interest. The library is the async Modbus client for Thermia heat pumps on the Genesis platform and stays free of Home Assistant: the integration lives in [ha-thermia-genesis](https://github.com/klconsultancy/ha-thermia-genesis).

## Before you write code

Open an issue first for anything beyond a small fix, so we can agree on the approach before you spend time on it. Read [CONTEXT.md](CONTEXT.md) for the domain terms, [docs/design.md](docs/design.md) for the design and [docs/errata.md](docs/errata.md) for where the pump differs from Thermia's protocol document. Report security issues privately as described in [SECURITY.md](SECURITY.md).

## Development

The tools run in the repository's devcontainer, with [uv](https://docs.astral.sh/uv/), on a git worktree:

```sh
git config worktree.useRelativePaths true
git worktree add .worktrees/my-change -b my-change origin/main
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . uv run --directory .worktrees/my-change pytest
```

Changes are test-first, and coverage stays at 100% (line and branch). CI also runs `ruff format --check`, `ruff check` and `mypy` (strict); `uv run prek run -a` runs the same hooks locally. [AGENTS.md](AGENTS.md) describes the workflow in full.

Never write to a real heat pump from a test: use `modbus_connection`'s mock unit or an in-process `tmodbus` server.

## Pull requests

- Keep a pull request to one change, with tests.
- CI (lint, type check, tests on every supported Python version and on the lowest and newest `modbus-connection`, a build of the distribution, dependency review and CodeQL) must pass before merging.
- Pull requests are squash-merged, so the pull request title becomes the commit message on `main`. Write it as a [Conventional Commit](https://www.conventionalcommits.org/) with a short imperative description, such as `fix: read input 137 at scale 100`: release-please derives the next version and the changelog from these titles. Use `feat!:` or a `BREAKING CHANGE:` footer for a change that breaks the public API.

By contributing you agree that your contribution is licensed under the [MIT license](LICENSE), and you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

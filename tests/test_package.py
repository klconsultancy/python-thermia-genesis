from importlib.metadata import version

import thermia_genesis


def test_exposes_installed_version() -> None:
    assert thermia_genesis.__version__ == version("thermia-genesis")

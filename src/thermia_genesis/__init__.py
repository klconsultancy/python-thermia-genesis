"""Async library for Thermia heat pumps on the Genesis platform via Modbus."""

from importlib.metadata import version

from thermia_genesis._pump import ThermiaGenesis
from thermia_genesis.firmware import FirmwareVersion

__all__ = ["FirmwareVersion", "ThermiaGenesis", "__version__"]

__version__ = version("thermia-genesis")

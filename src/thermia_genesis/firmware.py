"""The control software version of the pump (input registers 311-313)."""

from typing import NamedTuple

# The firmware the register map is written for; docs/design.md (Scope).
SUPPORTED = (17, 1)


class FirmwareVersion(NamedTuple):
    """A firmware version: compare it as a tuple, print it as "17.1.11"."""

    major: int
    minor: int
    micro: int

    def __str__(self) -> str:
        """Format as "major.minor.micro"."""
        return f"{self.major}.{self.minor}.{self.micro}"

    @property
    def supported(self) -> bool:
        """Whether the register map is written for this major.minor version (17.1)."""
        return (self.major, self.minor) == SUPPORTED

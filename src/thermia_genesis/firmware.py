"""The control software version of the pump (input registers 311-313)."""

from typing import NamedTuple

# The firmware versions the register map is written for or checked against;
# docs/design.md (Scope).
SUPPORTED = frozenset({(17, 1), (18, 0)})


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
        """Whether the register map applies to this major.minor version (17.1 or 18.0)."""
        return (self.major, self.minor) in SUPPORTED

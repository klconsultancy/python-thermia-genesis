"""Check the 17.1 register map against the tables of the protocol document."""

import importlib
import inspect
import pkgutil
from collections import Counter
from pathlib import Path
from typing import NamedTuple

import pytest
from modbus_connection.model import Component
from modbus_connection.model.fields import CoilField, DiscreteInputField, NumberField

from thermia_genesis import v17_1
from thermia_genesis.v17_1 import ABSENT_SENSOR

PROTOCOL = Path(__file__).parents[1] / "docs/protocol/17.1"

# Chapters 4-9 group the registers per subsystem; each subsystem is a module of v17_1.
CHAPTERS = {
    "04-heat-pump-unit.md": "heat_pump_unit",
    "05-heat.md": "heat",
    "06-tap-water.md": "tap_water",
    "07-cooling.md": "cooling",
    "08-pool.md": "pool",
    "09-electric-meter.md": "electric_meter",
}

# Registers whose subsystem the chapters don't give (or that we group differently),
# as agreed in docs/design.md (Register map).
ASSIGNED = {
    ("holding", 105): "cooling",
    ("holding", 106): "cooling",
    ("discrete", 47): "cooling",
    ("discrete", 238): "cooling",
    ("discrete", 242): "cooling",
    ("holding", 0): "status",
    **{("input", address): "status" for address in (1, 2, 55, 56, 62, 63, 64, 65, 66)},
    **{("input", address): "heat_pump_unit" for address in (143, 145, 146, 160, 161, 162, 163)},
    ("coil", 40): "heat_pump_unit",
    ("holding", 124): "heat_pump_unit",
    ("holding", 125): "heat_pump_unit",
}

# Subsystems whose registers are all in the map.
COMPLETE = ["heat_pump_unit"]


class DocumentedRegister(NamedTuple):
    unit: str
    scale: int
    description: str


def space_of(de_facto_address: int) -> str:
    if de_facto_address >= 40001:
        return "holding"
    if de_facto_address >= 30001:
        return "input"
    if de_facto_address >= 10001:
        return "discrete"
    return "coil"


def read_table(path: Path) -> dict[tuple[str, int], DocumentedRegister]:
    """The register rows of a chapter, keyed by register space and zero-based address."""
    registers: dict[tuple[str, int], DocumentedRegister] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not cells[3].isdigit():
            continue  # not a register row: prose, header or separator
        key = (space_of(int(cells[4])), int(cells[3]))
        registers[key] = DocumentedRegister(cells[1], int(cells[5]), cells[6])
    return registers


DOCUMENTED = read_table(PROTOCOL / "03-address-list.md")


def documented_subsystems() -> dict[tuple[str, int], str]:
    subsystems: dict[tuple[str, int], str] = {}
    for chapter, name in CHAPTERS.items():
        subsystems.update(dict.fromkeys(read_table(PROTOCOL / chapter), name))
    subsystems.update(ASSIGNED)
    return subsystems


SUBSYSTEMS = documented_subsystems()


class MappedRegister(NamedTuple):
    subsystem: str
    space: str
    address: int
    scale: int
    half: str | None = None  # "MSB" or "LSB" for one word of a 32-bit value
    nan: frozenset[int] | None = None  # raw values that decode as no value


def components() -> list[tuple[str, type[Component]]]:
    """Every component of the map, with the subsystem module it is declared in."""
    found = []
    for module_info in pkgutil.iter_modules(v17_1.__path__):
        module = importlib.import_module(f"{v17_1.__name__}.{module_info.name}")
        found += [
            (module_info.name, member)
            for member in vars(module).values()
            if inspect.isclass(member)
            and issubclass(member, Component)
            and member.__module__ == module.__name__
        ]
    return found


def mapped_registers() -> dict[str, list[MappedRegister]]:
    """Every register the map reads, keyed by ``Component.field``."""
    mapped: dict[str, list[MappedRegister]] = {}
    for subsystem, component in components():
        for name, field in component.declared_fields.items():
            key = f"{component.__name__}.{name}"
            if isinstance(field, CoilField):
                mapped[key] = [MappedRegister(subsystem, "coil", field.address, 1)]
            elif isinstance(field, DiscreteInputField):
                mapped[key] = [MappedRegister(subsystem, "discrete", field.address, 1)]
            else:
                # The map stores the multiplier (0.01); the document the divisor (100).
                scale = round(1 / getattr(field, "scale", 1.0))
                nan = getattr(field, "nan", None)
                halves: list[str | None] = [None] * field.count
                if isinstance(field, NumberField) and field.count == 2:
                    halves = ["MSB", "LSB"] if field.word_order == "big" else ["LSB", "MSB"]
                mapped[key] = [
                    MappedRegister(
                        subsystem,
                        component.register_space,
                        field.address + offset,
                        scale,
                        half,
                        nan,
                    )
                    for offset, half in enumerate(halves)
                ]
    return mapped


MAPPED = mapped_registers()


def test_reads_every_table_of_the_address_list() -> None:
    per_space = Counter(space for space, _ in DOCUMENTED)

    assert per_space == {"coil": 26, "discrete": 68, "input": 99, "holding": 66}


def test_finds_the_mapped_registers() -> None:
    # Without this, an empty map would skip the parametrized check instead of failing.
    assert MAPPED


@pytest.mark.parametrize("name", sorted(MAPPED))
def test_mapped_register_matches_address_list(name: str) -> None:
    for register in MAPPED[name]:
        key = (register.space, register.address)
        documented = DOCUMENTED.get(key)

        assert documented is not None, f"{register.space} {register.address} is not documented"
        assert register.scale == documented.scale, documented.description
        assert register.subsystem == SUBSYSTEMS.get(key), documented.description
        if register.half:
            assert documented.description.endswith(f"({register.half})"), documented.description
        else:
            # A half of a 32-bit value read on its own wraps at 65535.
            assert not documented.description.endswith(("(MSB)", "(LSB)")), documented.description
        if (documented.unit, documented.scale) == ("°C", 100):
            assert register.nan is not None, documented.description
            assert ABSENT_SENSOR in register.nan, documented.description


@pytest.mark.parametrize("subsystem", COMPLETE)
def test_maps_every_register_of_a_complete_subsystem(subsystem: str) -> None:
    expected = {key for key, name in SUBSYSTEMS.items() if name == subsystem}
    mapped = {
        (register.space, register.address)
        for registers in MAPPED.values()
        for register in registers
        if register.subsystem == subsystem
    }

    assert sorted(expected - mapped) == []

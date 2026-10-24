"""Check the 17.1 register map against chapter 3 of the protocol document."""

import inspect
import re
from collections import Counter
from pathlib import Path
from typing import NamedTuple

import pytest
from modbus_connection.model import Component
from modbus_connection.model.fields import CoilField, DiscreteInputField, NumberField

from thermia_genesis import v17_1
from thermia_genesis.v17_1 import ABSENT_SENSOR

ADDRESS_LIST = Path(__file__).parents[1] / "docs/protocol/17.1/03-address-list.md"

# Chapter 3 has one table per register space, under these section headings.
SPACES = {"3.1": "coil", "3.2": "discrete", "3.3": "input", "3.4": "holding"}


class DocumentedRegister(NamedTuple):
    unit: str
    scale: int
    description: str


def documented_registers() -> dict[tuple[str, int], DocumentedRegister]:
    registers: dict[tuple[str, int], DocumentedRegister] = {}
    space = ""
    for line in ADDRESS_LIST.read_text(encoding="utf-8").splitlines():
        if heading := re.match(r"## (3\.\d) ", line):
            space = SPACES[heading.group(1)]
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not cells[3].isdigit():
            continue  # not a register row: prose, header or separator
        registers[space, int(cells[3])] = DocumentedRegister(cells[1], int(cells[5]), cells[6])
    return registers


DOCUMENTED = documented_registers()


class MappedRegister(NamedTuple):
    space: str
    address: int
    scale: int
    half: str | None = None  # "MSB" or "LSB" for one word of a 32-bit value
    nan: frozenset[int] | None = None  # raw values that decode as no value


def mapped_registers() -> dict[str, list[MappedRegister]]:
    """Every register the map reads, keyed by ``Component.field``."""
    mapped: dict[str, list[MappedRegister]] = {}
    for component in vars(v17_1).values():
        if not (inspect.isclass(component) and issubclass(component, Component)):
            continue
        for name, field in component.declared_fields.items():
            key = f"{component.__name__}.{name}"
            if isinstance(field, CoilField):
                mapped[key] = [MappedRegister("coil", field.address, 1)]
            elif isinstance(field, DiscreteInputField):
                mapped[key] = [MappedRegister("discrete", field.address, 1)]
            else:
                # The map stores the multiplier (0.01); the document the divisor (100).
                scale = round(1 / getattr(field, "scale", 1.0))
                nan = getattr(field, "nan", None)
                halves: list[str | None] = [None] * field.count
                if isinstance(field, NumberField) and field.count == 2:
                    halves = ["MSB", "LSB"] if field.word_order == "big" else ["LSB", "MSB"]
                mapped[key] = [
                    MappedRegister(
                        component.register_space, field.address + offset, scale, half, nan
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
        documented = DOCUMENTED.get((register.space, register.address))

        assert documented is not None, f"{register.space} {register.address} is not documented"
        assert register.scale == documented.scale, documented.description
        if register.half:
            assert documented.description.endswith(f"({register.half})"), documented.description
        else:
            # A half of a 32-bit value read on its own wraps at 65535.
            assert not documented.description.endswith(("(MSB)", "(LSB)")), documented.description
        if (register.space, documented.unit, documented.scale) == ("input", "°C", 100):
            assert register.nan is not None, documented.description
            assert ABSENT_SENSOR in register.nan, documented.description

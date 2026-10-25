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
from thermia_genesis.subsystem import Subsystem
from thermia_genesis.v17_1 import ABSENT_SENSOR, ABSENT_SENSOR_AT_SCALE_10

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

# Every subsystem, as a module of v17_1.
SUBSYSTEM_NAMES = sorted({*CHAPTERS.values(), *ASSIGNED.values()})


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


type Key = tuple[str, int]  # register space and zero-based address


def read_rows(path: Path) -> list[tuple[Key, DocumentedRegister]]:
    """The register rows of a chapter, in document order."""
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not cells[3].isdigit():
            continue  # not a register row: prose, header or separator
        key = (space_of(int(cells[4])), int(cells[3]))
        rows.append((key, DocumentedRegister(cells[1], int(cells[5]), cells[6])))
    return rows


def read_table(path: Path) -> dict[Key, DocumentedRegister]:
    return dict(read_rows(path))


ADDRESS_LIST = read_table(PROTOCOL / "03-address-list.md")

# Rows of chapters 4-9 that differ from chapter 3, each recorded in docs/errata.md.
CHAPTER_ERRATA = {
    ("04-heat-pump-unit.md", ("coil", 25)): "scale 100 for a coil",
    ("06-tap-water.md", ("coil", 6)): "not in chapter 3",
    ("06-tap-water.md", ("coil", 14)): "not in chapter 3",
    ("06-tap-water.md", ("discrete", 52)): "not in chapter 3",
    ("06-tap-water.md", ("discrete", 223)): "not in chapter 3",
    ("06-tap-water.md", ("input", 45)): "not in chapter 3",
    ("06-tap-water.md", ("input", 47)): "listed twice, also as HGW mix valve position",
    ("07-cooling.md", ("input", 137)): "unit on/off for an opening degree",
    ("08-pool.md", ("input", 119)): "not in chapter 3",
    ("08-pool.md", ("input", 120)): "not in chapter 3",
    ("08-pool.md", ("holding", 58)): "unit °C, where chapter 3 says %",
}

# Registers documented only in chapters 4-9 count as documented too (see errata.md).
DOCUMENTED = ADDRESS_LIST | {
    key: register
    for chapter in CHAPTERS
    for key, register in read_rows(PROTOCOL / chapter)
    if (chapter, key) in CHAPTER_ERRATA and key not in ADDRESS_LIST
}

# Units the errata take from another source than chapter 3.
UNIT_ERRATA = {
    ("holding", 58): "°C",  # chapter 8; the reference pump reads 26.00
    # The display setting "Gewenste koelaanvoer min." (°C) changes holding 30, not 105.
    ("holding", 30): "°C",
    # The display shows 300 as "0:05:00", so the gear shift delays are in seconds.
    ("holding", 61): "s",
    ("holding", 62): "s",
    ("holding", 63): "s",
}
DOCUMENTED |= {key: DOCUMENTED[key]._replace(unit=unit) for key, unit in UNIT_ERRATA.items()}


def documented_subsystems() -> dict[Key, str]:
    subsystems: dict[Key, str] = {}
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
            (module_info.name, component)
            for member in vars(module).values()
            if inspect.isclass(member)
            and issubclass(member, Subsystem)
            and member.__module__ == module.__name__
            for component in member.component_types.values()
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
    per_space = Counter(space for space, _ in ADDRESS_LIST)

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
        # 200.0 °C means "no sensor": 20000 at scale 100, 2000 at scale 10.
        absent = {100: ABSENT_SENSOR, 10: ABSENT_SENSOR_AT_SCALE_10}.get(documented.scale)
        if documented.unit == "°C" and absent is not None:
            assert register.nan is not None, documented.description
            assert absent in register.nan, documented.description


def test_every_documented_register_belongs_to_a_subsystem() -> None:
    assert sorted(DOCUMENTED.keys() - SUBSYSTEMS.keys()) == []


@pytest.mark.parametrize("subsystem", SUBSYSTEM_NAMES)
def test_maps_every_register_of_the_subsystem(subsystem: str) -> None:
    expected = {key for key, name in SUBSYSTEMS.items() if name == subsystem}
    mapped = {
        (register.space, register.address)
        for registers in MAPPED.values()
        for register in registers
        if register.subsystem == subsystem
    }

    assert sorted(expected - mapped) == []


# Each component holds one Modbus register space, named after it.
SPACE_OF_COMPONENT = {
    "Coils": "coil",
    "DiscreteInputs": "discrete",
    "InputRegisters": "input",
    "HoldingRegisters": "holding",
}


@pytest.mark.parametrize(
    "component", [component for _, component in components()], ids=lambda c: c.__name__
)
def test_component_holds_the_register_space_it_is_named_after(
    component: type[Component],
) -> None:
    suffix = next((s for s in SPACE_OF_COMPONENT if component.__name__.endswith(s)), None)
    assert suffix is not None, f"{component.__name__} is not named after a register space"
    spaces = {
        register.space
        for name in component.declared_fields
        for register in MAPPED[f"{component.__name__}.{name}"]
    }

    assert spaces == {SPACE_OF_COMPONENT[suffix]}


# Unscaled numbers that can be negative, and why. Every other unscaled number is unsigned,
# so a count, timer or meter value above 32767 doesn't turn negative (docs/design.md).
SIGNED = {
    ("input", 36): "season integral; the reference pump reads -150",
    ("input", 131): "season integral; the reference pump reads -150",
    ("input", 319): "temperature in °C",
    **dict.fromkeys(
        [("input", 78), ("input", 79), ("input", 80)],
        "phase power at the house connection; export may be negative",
    ),
    ("holding", 75): "PID sum; the reference pump reads -6",
}


def unscaled_numbers() -> list[tuple[str, int, bool]]:
    """Space, address and signedness of every unscaled 16-bit number in the map."""
    return [
        (component.register_space, field.address, field.signed)
        for _, component in components()
        for field in component.declared_fields.values()
        if isinstance(field, NumberField)
        and field.count == 1
        and field.scale == 1
        and field.convert is None
    ]


@pytest.mark.parametrize(("space", "address", "signed"), unscaled_numbers(), ids=str)
def test_unscaled_number_is_unsigned_unless_it_can_be_negative(
    space: str, address: int, *, signed: bool
) -> None:
    assert signed == ((space, address) in SIGNED), DOCUMENTED[space, address].description


def same_unit(chapter_unit: str, address_list_unit: str) -> bool:
    """Whether two units agree; a chapter often leaves the unit out or writes on/off."""
    words = {"active/ inactive": "on/off"}
    chapter, address_list = (
        words.get(u.lower(), u.lower()) for u in (chapter_unit, address_list_unit)
    )
    return not chapter or chapter == address_list


def normalized(description: str) -> str:
    """A description with the whitespace differences between the chapters removed."""
    return " ".join(description.split()).replace(" )", ")")


def differs_from_address_list(chapter: str, key: Key, register: DocumentedRegister) -> bool:
    documented = ADDRESS_LIST.get(key)
    return (
        documented is None
        or register.scale != documented.scale
        or normalized(register.description) != normalized(documented.description)
        or not same_unit(register.unit, documented.unit)
        or [k for k, _ in read_rows(PROTOCOL / chapter)].count(key) > 1
    )


@pytest.mark.parametrize("chapter", CHAPTERS)
def test_chapter_agrees_with_address_list(chapter: str) -> None:
    differing = {
        key
        for key, register in read_rows(PROTOCOL / chapter)
        if differs_from_address_list(chapter, key, register)
    }

    assert differing == {key for (name, key) in CHAPTER_ERRATA if name == chapter}


# What the "Units" column holds for values without a physical unit.
NOT_A_UNIT = {"", "enum", "bitfield", "step", "on/off", "active/ inactive"}


def field_units() -> list[tuple[str, int, str | None]]:
    """Space, address and declared unit of every register field in the map."""
    return [
        (component.register_space, field.address, getattr(field, "unit", None))
        for _, component in components()
        for field in component.declared_fields.values()
        if not isinstance(field, (CoilField, DiscreteInputField))
    ]


@pytest.mark.parametrize(("space", "address", "unit"), field_units(), ids=str)
def test_field_has_the_documented_unit(space: str, address: int, unit: str | None) -> None:
    documented = DOCUMENTED[space, address]
    if documented.unit not in NOT_A_UNIT:
        assert unit == documented.unit, documented.description

"""Subsystems: the fields of one part of the pump, whatever register space they live in.

A subsystem declares each field once, wrapped in its Modbus register space::

    class Heat(Subsystem):
        enable_mix_valve_1 = coil(11)
        system_supply_line_temperature = input_register(gauge(12, 0.01))

The class builds one ``modbus_connection`` component per register space it uses, and each
field reads its value from that component. Callers see typed attributes only.
"""

import math
from collections.abc import Callable
from enum import IntEnum
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Never, NoReturn, overload

from modbus_connection import ModbusUnit
from modbus_connection.model import Component
from modbus_connection.model import coil as _coil
from modbus_connection.model import discrete_input as _discrete_input
from modbus_connection.model.fields import (
    CoilField,
    DiscreteInputField,
    RegisterField,
    WriteValidator,
)

type Space = Literal["coil", "discrete", "input", "holding"]

# The name of a subsystem's component per register space, after the class name.
COMPONENT_SUFFIXES: dict[Space, str] = {
    "coil": "Coils",
    "discrete": "DiscreteInputs",
    "input": "InputRegisters",
    "holding": "HoldingRegisters",
}


class Field[T]:
    """A field of a subsystem, read from the component of its register space."""

    def __init__(
        self, space: Space, field: RegisterField[T] | CoilField | DiscreteInputField
    ) -> None:
        """Wrap a ``modbus_connection`` field declared in ``space``."""
        self.space = space
        self.field = field

    def __set_name__(self, owner: type, name: str) -> None:
        """Remember the attribute name, which is also the field's name in its component."""
        self.name = name

    @property
    def writable(self) -> bool:
        """Whether ``Subsystem.write`` can write the field: a writable coil or holding register."""
        return self.space in {"coil", "holding"} and bool(self.field.writable)

    def check(self, value: object) -> None:
        """Refuse a value of the wrong type, or one the register can't represent exactly.

        Raises ``TypeError`` for a coil value that isn't a ``bool`` or a register value that
        is, and ``ValueError`` for a value that isn't finite or isn't a whole multiple of the
        register's resolution, which the encoding would otherwise round.
        """
        if self.space == "coil":
            if not isinstance(value, bool):
                msg = f"{self.name} takes a bool, got {value!r}"
                raise TypeError(msg)
            return
        if isinstance(value, bool) or not isinstance(value, int | float):
            msg = f"{self.name} takes a number, got {value!r}"
            raise TypeError(msg)
        if not math.isfinite(value):
            msg = f"{self.name} must be a finite number, got {value}"
            raise ValueError(msg)
        resolution = getattr(self.field, "scale", 1)
        steps = (value - getattr(self.field, "offset", 0)) / resolution
        if not math.isclose(steps, round(steps), abs_tol=1e-6):
            msg = f"{self.name} must be a multiple of {resolution:g}, got {value}"
            raise ValueError(msg)

    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type | None = ...) -> "Field[T]": ...

        @overload
        def __get__(self, obj: object, objtype: type | None = ...) -> T | None: ...

    def __get__(self, obj: object, objtype: type | None = None) -> Any:
        """Return the field's value, read from the component of its register space."""
        if obj is None:
            return self
        return getattr(obj.components[self.space], self.name)  # type: ignore[attr-defined]

    def __set__(self, obj: object, value: Never) -> NoReturn:
        """Refuse assignment: a write is I/O, so it goes through ``Subsystem.write``."""
        if self.writable:
            msg = f"{self.name} can't be assigned; use await {type(obj).__name__}.write()"
        else:
            msg = f"{self.name} is read-only"
        raise AttributeError(msg)


def between(low: float, high: float) -> WriteValidator:
    """Accept a value from ``low`` to ``high``, both included."""

    def validate(value: float) -> float:
        if not low <= value <= high:
            msg = f"must be {low}-{high}, got {value}"
            raise ValueError(msg)
        return value

    return validate


def member_of[E: IntEnum](enum_type: type[E]) -> Callable[[int], E]:
    """Accept a member of ``enum_type``, or the value of one."""

    def validate(value: int) -> E:
        try:
            return enum_type(value)
        except ValueError:
            names = ", ".join(member.name for member in enum_type)
            msg = f"must be one of {names}, got {value}"
            raise ValueError(msg) from None

    return validate


def coil(address: int, *, writable: bool | WriteValidator = False) -> Field[bool]:
    """Declare a coil (FC01, written with FC05) of the subsystem."""
    return Field("coil", _coil(address, writable=writable))


def discrete_input(address: int) -> Field[bool]:
    """Declare a discrete input (FC02) of the subsystem."""
    return Field("discrete", _discrete_input(address))


def input_register[T](field: RegisterField[T]) -> Field[T]:
    """Declare an input register field (FC04) of the subsystem."""
    return Field("input", field)


def holding_register[T](field: RegisterField[T]) -> Field[T]:
    """Declare a holding register field (FC03) of the subsystem."""
    return Field("holding", field)


class Subsystem:
    """A part of the pump: its fields, read from one component per register space."""

    # The component class of each register space the subsystem uses.
    component_types: ClassVar[dict[Space, type[Component]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Build one component class per register space from the declared fields."""
        super().__init_subclass__(**kwargs)
        fields: dict[Space, dict[str, Any]] = {}
        # Base classes first, so a subclass keeps the fields it inherits and can redeclare one.
        for klass in reversed(cls.__mro__):
            for name, value in vars(klass).items():
                if isinstance(value, Field):
                    fields.setdefault(value.space, {})[name] = value.field
        cls.component_types = {
            space: type(
                f"{cls.__name__}{COMPONENT_SUFFIXES[space]}",
                (Component,),
                {"__module__": cls.__module__, **space_fields}
                | ({"register_space": space} if space in {"input", "holding"} else {}),
            )
            for space, space_fields in fields.items()
        }

    def __init__(self, unit: ModbusUnit) -> None:
        """Create the subsystem's components on ``unit``."""
        self.components: dict[Space, Component] = {
            space: component_type(unit) for space, component_type in self.component_types.items()
        }

    async def write[T](self, field: Field[T], value: T) -> None:
        """Write ``value`` to ``field`` on the pump.

        The field keeps its old value until the next update reads back what the pump
        accepted. Raises ``AttributeError`` for a read-only field or one the subsystem doesn't
        declare, ``TypeError`` for a value of the wrong type (see ``Field.check``), and
        ``ValueError`` for a value the field's validator refuses or its register can't hold.
        Nothing is written when it raises.
        """
        if getattr(type(self), field.name, None) is not field:
            msg = f"{type(self).__name__} has no field {field.name}"
            raise AttributeError(msg)
        if not field.writable:
            msg = f"{field.name} is read-only"
            raise AttributeError(msg)
        field.check(value)
        try:
            await self.components[field.space].write(field.name, value)
        except (ValueError, OverflowError) as err:
            msg = f"{field.name} {err}"
            raise ValueError(msg) from err

"""Subsystems: the fields of one part of the pump, whatever register space they live in.

A subsystem declares each field once, wrapped in its Modbus register space::

    class Heat(Subsystem):
        enable_mix_valve_1 = coil(11)
        system_supply_line_temperature = input_register(gauge(12, 0.01))

The class builds one ``modbus_connection`` component per register space it uses, and each
field reads its value from that component. Callers see typed attributes only.
"""

from typing import TYPE_CHECKING, Any, ClassVar, Literal, Never, NoReturn, overload

from modbus_connection import ModbusUnit
from modbus_connection.model import Component
from modbus_connection.model import coil as _coil
from modbus_connection.model import discrete_input as _discrete_input
from modbus_connection.model.fields import CoilField, DiscreteInputField, RegisterField

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
        """Refuse assignment: the map is read-only until the write API (#19)."""
        msg = f"{self.name} is read-only"
        raise AttributeError(msg)


def coil(address: int) -> Field[bool]:
    """Declare a coil (FC01) of the subsystem."""
    return Field("coil", _coil(address))


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

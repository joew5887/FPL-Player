from dataclasses import fields
from typing import Any, Generic, TypeVar


t = TypeVar("t")
b = TypeVar("b", int, float)


class Attribute(Generic[t]):
    def __init__(self, values: list[t], attr_name: str):
        self.values = values
        self.__attr_name = attr_name

    def __str__(self) -> str:
        return f"{self.__attr_name} - {self.__values}"

    @property
    def values(self) -> list[t]:
        return self.__values

    @values.setter
    def values(self, new_values: list[t]) -> None:
        self.__values = new_values
        self.__edit_values()

    def __edit_values(self) -> None:
        pass


class CategoricalVar(Attribute[t]):
    def __init__(self, values: list[t], attr_name: str):
        super().__init__(values, attr_name)


class ContinuousVar(Attribute[b]):
    def __init__(self, values: list[b], attr_name: str):
        super().__init__(values, attr_name)

    def __edit_values(self) -> None:
        super().__edit_values()

    @property
    def average(self) -> float:
        return sum(self.values) / len(self.values)


def all_attributes_present(class_, new_instance: dict[str, Any]) -> bool:
    """Checks if `new_instance` contains all the attributes of `class_`.

    Parameters
    ----------
    class_ : _type_
        A class with the `@dataclass` decorator.
    new_instance : dict[str, Any]
        Attribute name to the value.

    Returns
    -------
    bool
        True if `new_instance` contains all the necessary attributes of `class_`.
    """
    actual_attr_names = set(all_field_names(class_))
    found_attr_names = set(new_instance.keys())

    if actual_attr_names == found_attr_names:
        return True
    elif actual_attr_names.issubset(found_attr_names):
        return True
    else:  # More values in actual_attr_names
        return False


def all_field_names(class_) -> list[str]:
    """Gets all field names for a given class.

    Parameters
    ----------
    class_ : _type_
        A class with the `@dataclass` decorator.

    Returns
    -------
    list[str]
        All field names for `class_`.
    """
    class_attrs = fields(class_)

    return [attr.name for attr in class_attrs]

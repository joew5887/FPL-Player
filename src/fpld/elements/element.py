from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TypeVar, overload, Union, Generic
from ..util import API


elem_type = TypeVar("elem_type", bound="Element")


class Element(ABC, Generic[elem_type]):
    _DEFAULT_ID = "code"

    def __init__(self, **attr_to_value):
        for col, attr in attr_to_value.items():
            setattr(self, col, attr)

    @overload
    def __eq__(self, other: Element) -> bool: ...

    def __eq__(self, other: Any) -> NotImplementedError:
        if isinstance(other, type(self)):
            return self.unique_id == other.unique_id

        return NotImplementedError

    @overload
    def __lt__(self, other: Element) -> bool: ...

    def __lt__(self, other: Any) -> NotImplementedError:
        if isinstance(other, type(self)):
            return self.unique_id < other.unique_id

        return NotImplementedError

    @overload
    def __gt__(self, other: Element) -> bool: ...

    def __gt__(self, other: Any) -> NotImplementedError:
        if isinstance(other, type(self)):
            return self.unique_id > other.unique_id

        return NotImplementedError

    @overload
    def __le__(self, other: Element) -> bool: ...

    def __le__(self, other: Any) -> NotImplementedError:
        if isinstance(other, type(self)):
            return self.unique_id <= other.unique_id

        return NotImplementedError

    @overload
    def __ge__(self, other: Element) -> bool: ...

    def __ge__(self, other: Any) -> NotImplementedError:
        if isinstance(other, type(self)):
            return self.unique_id >= other.unique_id

        return NotImplementedError

    def __str__(self) -> str:
        return f"{self.unique_id}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(unique_id='{self.unique_id}')"

    @ property
    def unique_id(self) -> Union[int, AttributeError]:
        id_col = type(self).unique_id_col
        id_ = getattr(self, id_col, None)

        if id_ is None:
            raise AttributeError(
                (
                    f"'{id_col}' not in object. "
                    "Unique ID could not be found."
                )
            )

        return id_

    @ classmethod
    @ property
    def unique_id_col(cls) -> str:
        return cls._DEFAULT_ID

    @classmethod
    @property
    @abstractmethod
    def api_link(cls) -> str:
        return

    @classmethod
    @property
    @abstractmethod
    def get_api(cls) -> dict:
        return

    @classmethod
    def get_from_api(cls, method_: str = "all", **attr_to_value: dict[str, Any]) -> list[elem_type]:
        METHOD_CHOICES = ["all", "or"]

        if method_ not in METHOD_CHOICES:
            raise Exception(f"method_ must be in {METHOD_CHOICES}")

        if method_ == "all":
            func = all
        elif method_ == "or":
            func = any

        elements = cls.get_api
        elements_found = []

        for elem in elements:
            conditions = []

            for col, attr in attr_to_value.items():
                if col not in elem:
                    raise KeyError(
                        f"'{col}' not in attributes.\nUse: {elem.keys()}")

                conditions.append(elem[col] == attr)

            if func(conditions):
                elements_found.append(elem)

        return [cls(**elem) for elem in elements_found]

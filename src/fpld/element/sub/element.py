from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, overload, Union


class Element(ABC):
    __DEFAULT_ID = "code"

    @overload
    def __eq__(self, other: Element) -> bool: ...

    def __eq__(self, other: Any) -> NotImplementedError:
        if isinstance(type(self), other):
            return self.unique_id == other.unique_id

        return NotImplementedError

    @overload
    def __lt__(self, other: Element) -> bool: ...

    def __lt__(self, other: Any) -> NotImplementedError:
        if isinstance(type(self), other):
            other_elem: Element = other_elem
            return self.unique_id < other_elem.unique_id

        return NotImplementedError

    @overload
    def __gt__(self, other: Element) -> bool: ...

    def __gt__(self, other: Any) -> NotImplementedError:
        if isinstance(type(self), other):
            other_elem: Element = other_elem
            return self.unique_id > other.unique_id

        return NotImplementedError

    @overload
    def __le__(self, other: Element) -> bool: ...

    def __le__(self, other: Any) -> NotImplementedError:
        if isinstance(type(self), other):
            other_elem: Element = other
            return self.unique_id <= other_elem.unique_id

        return NotImplementedError

    @overload
    def __ge__(self, other: Element) -> bool: ...

    def __ge__(self, other: Any) -> NotImplementedError:
        if isinstance(type(self), other):
            other_elem: Element = other
            return self.unique_id >= other_elem.unique_id

        return NotImplementedError

    def __str__(self) -> str:
        return f"{self.unique_id}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(unique_id='{self.unique_id}')"

    @ property
    def unique_id(self) -> Union[int, AttributeError]:
        id_col = type(self).unique_id_col

        if id_col not in self.stats:
            raise AttributeError(
                (
                    f"'{id_col}' not in stats. "
                    "Unique ID could not be found."
                )
            )

        raise NotImplementedError
        return

    @ classmethod
    @ property
    def unique_id_col(cls) -> str:
        return cls.__DEFAULT_ID

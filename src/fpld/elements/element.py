from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Union, Generic, Optional, overload
from dataclasses import fields
from ..util import all_attributes_present
from functools import cache


elem_type = TypeVar("elem_type", bound="Element")


class Element(ABC, Generic[elem_type]):
    _DEFAULT_ID = "id"

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

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        return new_instance

    @classmethod
    def _add_attrs(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        return new_instance

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
    def from_dict(cls, new_instance: dict[str, Any]) -> elem_type:
        class_fields = fields(cls)
        field_names = {f.name for f in class_fields}
        new_instance = cls._add_attrs(new_instance)

        if all_attributes_present(cls, new_instance):
            required_attrs = {attr: new_instance[attr]
                              for attr in field_names}
            edited_attrs = cls.__pre_init__(required_attrs)
            return cls(**edited_attrs)

        raise KeyError(
            f"Missing: {field_names.difference(set(new_instance.keys()))}")

    @classmethod
    @cache
    @overload
    def get_by_id(cls, id_: int) -> Optional[elem_type]: ...

    @classmethod
    @cache
    @overload
    def get_by_id(cls, id_: str) -> Optional[elem_type]: ...

    @classmethod
    @cache
    def get_by_id(cls, id_: Any) -> Optional[elem_type]:
        """Get an element by their unique id.

        Parameters
        ----------
        id_ : Any
            ID of element to find.

        Returns
        -------
        Optional[elem_type]
            The found element. May return None if no element has been found.

        Raises
        ------
        Exception
            If more than one element was found, ID should be unique.
        """
        filter_ = {cls.unique_id_col: id_}
        element = cls.get(**filter_)

        if len(element) > 1:
            raise Exception(f"Expected only one element, got {len(element)}.")
        elif len(element) == 0:
            return None
        else:
            return element[0]

    @classmethod
    @cache
    def get(cls, *, method_: str = "all", **attr_to_value: dict[str, Any]) -> list[elem_type]:
        """Get all elements from the relevant API by filters.

        Parameters
        ----------
        method_ : str, optional
            Return elements that satisfy all the filters or any of them, by default "all"

        Returns
        -------
        list[elem_type]
            All elements found in search.

        Raises
        ------
        Exception
            Invalid method choice.
        KeyError
            If any attribute name passed as kwargs is not an attribute.
        """

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

        return [cls.from_dict(elem) for elem in elements_found]

    @classmethod
    def top_n_elements(cls, col_by: str, n: int, filters: dict[str, Any], descending: bool = True) -> list[elem_type]:
        """Gets the highest (or lowest) n ranked elements by a given column and filters.

        Example
        -------

        ```
        > fpld.Player.top_n_elements("total_points", 10, {"team": 17})
        [Son, Kane, Lloris, Dier, Reguilón]
        ```

        Parameters
        ----------
        col_by : str
            Attribute to order by.
        n : int
            Number of elements to return. If elements found is less than n, it returns all elements found.
        filters: dict[str, Any]
            Filters to apply to top n elements where the attribute is the key and the requested value is the value
        descending : bool, optional
            How to sort list, by default True

        Returns
        -------
        list[elem_type]
            Top n elements found.
        """

        filtered_elems = cls.get(**filters)
        sorted_filtered_elems = \
            sorted(filtered_elems, key=lambda e: getattr(
                e, col_by), reverse=descending)

        return sorted_filtered_elems[:n]

    @classmethod
    def top_n_all_elements(cls, col_by: str, n: int, descending: bool = True) -> list[elem_type]:
        """Gets the highest (or lowest) n ranked elements by a given column.

        Example
        -------

        ```
        > fpld.Player.top_n_all_elements("goals_scored", 10)
        [Salah, Son, Ronaldo, Jota, Mané, Toney, Kane, Saka, Zaha, De Bruyne]
        ```

        Parameters
        ----------
        col_by : str
            Attribute to order by.
        n : int
            Number of elements to return. If elements found is less than n, it returns all elements found.
        descending : bool, optional
            How to sort list, by default True

        Returns
        -------
        list[elem_type]
            Top n elements found.
        """

        return cls.top_n_elements(col_by, n, dict(), descending=descending)

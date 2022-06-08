from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Union, Generic, Optional, overload, Callable
from dataclasses import fields
from ..util import all_attributes_present
from functools import cache
from random import choice
import pandas as pd


elem_type = TypeVar("elem_type", bound="Element")


class Element(ABC, Generic[elem_type]):
    _DEFAULT_ID = "id"

    @ property
    def unique_id(self) -> int:
        """Returns unique ID for an object.

        Returns
        -------
        int
            Unique ID.

        Raises
        ------
        AttributeError
            If the ID cannot be found from the `unique_id_col`.
        """
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

    """@abstractmethod
    def info(self, *columns: tuple[str]) -> list:
        if len(columns) == 0:
            pass
            # Use default columns.

        return
        # Attributes from columns for element."""

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        """Edit current attributes from `new_instance` to the correct datatype
        for the object of the class it will become.

        Used before instantiating the object.

        Parameters
        ----------
        new_instance : dict[str, Any]
            All attributes of the new object.

        Returns
        -------
        dict[str, Any]
            Updated `new_instance` with the correct data types.
        """
        return new_instance

    @ classmethod
    @ property
    def unique_id_col(cls) -> str:
        """Attribute name that is a unique ID for any object of that class.

        Returns
        -------
        str
            Attribute name.
        """
        return cls._DEFAULT_ID

    @classmethod
    @property
    @abstractmethod
    def api_link(cls) -> str:
        """URL of API for objects of that class.

        Used in `cls.get_api` property.

        Returns
        -------
        str
            API URL.
        """
        return

    @classmethod
    @property
    @abstractmethod
    def get_api(cls) -> dict:
        """Data from API.

        Used by `get()` to find results.

        Returns
        -------
        dict
            Data for the clas.
        """
        return

    @classmethod
    def from_dict(cls, new_instance: dict[str, Any]) -> elem_type:
        """Converts dictionary of attributes to an object of the class.

        Parameters
        ----------
        new_instance : dict[str, Any]
            All attributes of the new object.

        Returns
        -------
        elem_type
            Object based on attributes and values from `new_instance`.

        Raises
        ------
        KeyError
            If `new_instance` is missing attributes from class.
        """
        class_fields = fields(cls)  # `cls` must be a dataclass.
        field_names = {f.name for f in class_fields}

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
    def get(cls, *, method_: str = "all", **
            attr_to_value: dict[str, Any]) -> list[elem_type]: ...

    @classmethod
    @cache
    def get(cls, *, method_: str = "all", **
            attr_to_value: dict[str, tuple[Any]]) -> list[elem_type]: ...

    @classmethod
    @cache
    def get(cls, *, method_: str = "all", **attr_to_value: Any) -> list[elem_type]:
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
        KeyError
            If any attribute name passed as kwargs is not an attribute.
        """

        # Method check
        func = _method_choice(method_)

        # Attr_to_value check
        for attr, values in attr_to_value.items():
            if not isinstance(values, tuple):
                attr_to_value[attr] = [values]

            temp = []

            for value in attr_to_value[attr]:
                if isinstance(value, Element):
                    temp.append(value.unique_id)
                else:
                    temp.append(value)

            attr_to_value[attr] = tuple(temp)

        elements = cls.get_api
        elements_found = []

        for elem in elements:
            conditions = []

            for attr, values in attr_to_value.items():
                if attr not in elem:
                    raise KeyError(
                        f"'{attr}' not in attributes.\nUse: {elem.keys()}")

                sub_conditions = []

                for value in values:
                    sub_conditions.append(elem[attr] == value)

                if any(sub_conditions):
                    conditions.append(True)
                else:
                    conditions.append(False)

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

    @classmethod
    def random(cls, **attr_to_value: dict[str, Any]) -> elem_type:
        """Gets random element based on filters passed.

        Returns
        -------
        elem_type
            Random element selected. May return None if filters produce no element.
        """

        choices = cls.get(**attr_to_value)

        if len(choices) == 0:
            return None

        return choice(choices)

    @classmethod
    def sort(cls, elements: list[elem_type], sort_by: str, *, reverse: bool = True) -> list[elem_type]:
        """Sorts a list of like elements by an attribute.

        Parameters
        ----------
        elements : list[elem_type]
            Elements to sort.
        sort_by : str
            Attribute name to sort `elements` by.
        reverse : bool, optional
            True if in descending order, by default True

        Returns
        -------
        list[elem_type]
            `elements` sorted by `sort_by`.
        """
        elements_sorted = sorted(elements, key=lambda elem: getattr(
            elem, sort_by), reverse=reverse)

        return elements_sorted

    @classmethod
    def as_df(cls, elements: list[elem_type], *attributes: tuple[str]) -> pd.DataFrame:
        df_rows = [[getattr(element, attr) for attr in attributes]
                   for element in elements]

        df = pd.DataFrame(df_rows, index=list(
            range(1, len(elements) + 1)), columns=attributes)

        return df


def _method_choice(method_: str) -> Callable:
    """Checks if method choice passed from `get` is acceptable.

    Parameters
    ----------
    method_ : str
        Choice of applying conditions. E.g. `all()`,  `any()`.

    Returns
    -------
    Callable
        Either `any()` or `all()`.

    Raises
    ------
    Exception
        If a method choice is not recognised.
    """
    METHOD_CHOICES = ["all", "or"]

    if method_ not in METHOD_CHOICES:
        raise Exception(f"method_ must be in {METHOD_CHOICES}")

    if method_ == "all":
        func = all
    elif method_ == "or":
        func = any

    return func

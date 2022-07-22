from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, SupportsIndex, TypeVar, Generic, Optional, overload, Callable
from dataclasses import fields
from PyQt5.QtWidgets import QPushButton
from ..util import all_attributes_present, all_field_names, Percentile
from functools import cache
from random import choice
import pandas as pd


element = TypeVar("element", bound="Element")


class Element(ABC, Generic[element]):
    _DEFAULT_ID = "id"
    _api = None
    _DEFAULT_NAME = "name"

    def __str__(self) -> str:
        return getattr(self, type(self)._DEFAULT_NAME, None)

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

      # No type to prevent circular import
    def create_button(self, window) -> QPushButton:
        """Creates a QPushButton that opens a window for that element.

        Parameters
        ----------
        window : FPLElemWindow
            Displays element in gui.

        Returns
        -------
        QPushButton
            Access to `window` from another window.
        """
        button = QPushButton()
        button.setText(str(self))
        button.clicked.connect(lambda: self.open_gui(window))

        return button

    def open_gui(self, window) -> None:
        """Opens `window` with `self` passed.

        Parameters
        ----------
        window : FPLElemWindow
            Displays element in gui.
        """
        window(self)

    @property
    def info(self) -> str:
        """Full info for element.

        Returns
        -------
        str
            Element informaiton.
        """
        field_names = all_field_names(type(self))

        return "\n".join([f_name + ": " + str(getattr(self, f_name)) for f_name in field_names])

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
    @abstractmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        """Data from API.

        Used by `get_api()` to get API.

        Returns
        -------
        list[dict[str, Any]]
            Latest data for the class.
        """
        return

    @classmethod
    def get_api(cls, refresh_api: bool = False) -> list[dict[str, Any]]:
        """Gets API either online or stored in memory from previous use.

        Used by `get()` to find search results.

        Parameters
        ----------
        refresh_api : bool, optional
            Return the latest version from FPL website, by default False

        Returns
        -------
        list[dict[str, Any]]
            Data for the class.
        """
        if (refresh_api is True) or (cls._api is None):
            cls._api = cls.get_latest_api()

        return cls._api

    @classmethod
    def from_dict(cls, new_instance: dict[str, Any]) -> element:
        """Converts dictionary of attributes to an object of the class.

        Parameters
        ----------
        new_instance : dict[str, Any]
            All attributes of the new object.

        Returns
        -------
        element
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
    def get_by_id(cls, id_: int) -> Optional[element]: ...

    @classmethod
    @cache
    @overload
    def get_by_id(cls, id_: str) -> Optional[element]: ...

    @classmethod
    @cache
    def get_by_id(cls, id_: Any) -> Optional[element]:
        """Get an element by their unique id.

        Parameters
        ----------
        id_ : Any
            ID of element to find.

        Returns
        -------
        Optional[element]
            The found element. May return None if no element has been found.

        Raises
        ------
        Exception
            If more than one element was found, ID should be unique.
        """
        filter_ = {cls.unique_id_col: id_}
        element_group = cls.get(**filter_)

        if len(element_group) > 1:
            raise Exception(
                f"Expected only one element, got {len(element_group)}.")
        elif len(element_group) == 0:
            return None
        else:
            return element_group[0]

    @classmethod
    @cache
    def get(cls, *, method_: str = "all", **
            attr_to_value: dict[str, Any]) -> ElementGroup[element]: ...

    @classmethod
    @cache
    def get(cls, *, method_: str = "all", **
            attr_to_value: dict[str, tuple[Any]]) -> ElementGroup[element]: ...

    @classmethod
    @cache
    def get(cls, *, method_: str = "all", **attr_to_value: Any) -> ElementGroup[element]:
        """Get all elements from the relevant API by filters.

        Parameters
        ----------
        method_ : str, optional
            Return elements that satisfy all the filters or any of them, by default "all"

        Returns
        -------
        ElementGroup[element]
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

        elements = cls.get_api()
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

        return ElementGroup([cls.from_dict(elem) for elem in elements_found])


class ElementGroup(ABC, Generic[element]):
    def __init__(self, objects: Iterable[element]):
        objects_no_duplicates = set(objects)
        self.__objects = list(objects_no_duplicates)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} of {len(self)} elements."

    def __iter__(self) -> Iterator[element]:
        return iter(self.__objects)

    def __len__(self) -> int:
        return len(self.__objects)

    @overload
    def __add__(self, obj: ElementGroup[element]) -> ElementGroup[element]: ...

    def __add__(self, obj: Any) -> Any:
        if isinstance(obj, ElementGroup):
            if not self.is_compatible(obj):
                raise Exception("ElementGroups must have same type.")

            return ElementGroup[element](self.as_list() + obj.as_list())
        else:
            raise NotImplementedError

    @overload
    def __getitem__(self, idx: SupportsIndex) -> element: ...
    @overload
    def __getitem__(self, idx: slice) -> ElementGroup[element]: ...

    def __getitem__(self, idx: Any) -> Any:
        if isinstance(idx, slice):
            return ElementGroup(self.__objects[idx])
        elif isinstance(idx, SupportsIndex):
            return self.__objects[idx]
        else:
            raise NotImplementedError

    def as_list(self) -> list[element]:
        return [elem for elem in self]

    def string_list(self) -> list[str]:
        output = [str(elem) for elem in self]

        return output

    def top_n_elements(self, col_by: str, n: int, reverse: bool = True) -> ElementGroup:
        return ElementGroup(self.sort(col_by, reverse=reverse)[:n])

    def random(self) -> element:
        """Gets random element from objects list.

        Returns
        -------
        element
            Random element selected.
        """

        return choice(self.__objects)

    def as_df(self, *attributes: tuple[str]) -> pd.DataFrame:
        """Gets a list of like elements and puts them into a dataframe.

        With the chosen attributes as columns.

        Returns
        -------
        pd.DataFrame
            `elements` data in a dataframe.
        """

        df_rows = [[getattr(element, attr) for attr in attributes]
                   for element in self]

        df = pd.DataFrame(df_rows, index=list(
            range(1, len(self) + 1)), columns=attributes)

        return df

    def sort(self, sort_by: str, *, reverse: bool = True) -> ElementGroup[element]:
        """Sorts a list of like elements by an attribute.

        Parameters
        ----------
        sort_by : str
            Attribute name to sort `elements` by.
        reverse : bool, optional
            True if in descending order, by default True

        Returns
        -------
        list[element]
            `elements` sorted by `sort_by`.
        """
        elements_sorted = sorted(self.__objects, key=lambda elem: getattr(
            elem, sort_by), reverse=reverse)

        return ElementGroup(elements_sorted)

    def percentile(self, attr: str) -> Percentile:
        elements_to_attr = {elem: getattr(elem, attr) for elem in self}

        for attr_value in elements_to_attr.values():
            if not isinstance(attr_value, (int, float)):
                raise TypeError("Must be int or float.")

        return Percentile(elements_to_attr)

    def is_compatible(self, other: ElementGroup) -> bool:
        subtypes_found = []

        full_list = self.as_list() + other.as_list()

        for elem in full_list:
            if type(elem) not in subtypes_found:
                subtypes_found.append(type(elem))

                if len(subtypes_found) > 1:
                    return False

        return True


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
    else:
        func = any

    return func

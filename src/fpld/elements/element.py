from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, Optional, SupportsIndex, Type, TypeVar, Generic, Union, overload, Callable
from dataclasses import fields
from ..util import all_attributes_present, all_field_names, Percentile
from functools import cache
from random import choice, sample
import pandas as pd


element = TypeVar("element", bound="_Element[Any]")  # generic type of `Element`


class _Element(ABC, Generic[element]):
    """Template class for an FPL element.

    E.g. Players, Teams, Fixtures
    """

    UNIQUE_ID_COL: str = "id"
    _api = None
    _ATTR_FOR_STR: str = "name"

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

    def __str__(self) -> str:
        """Gets attribute called `cls._ATTR_FOR_STR`.

        Returns
        -------
        str
            Text name of element.
        """
        return str(getattr(self, type(self)._ATTR_FOR_STR))

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
        id_col: str = type(self).UNIQUE_ID_COL
        id_: int = getattr(self, id_col)
        '''id_: int = getattr(self, id_col, -1)

        if id_ == -1:
            raise AttributeError(
                (
                    f"'{id_col}' not in object. "
                    "Unique ID could not be found."
                )
            )'''

        return id_

    @classmethod
    @abstractmethod
    def api_link(cls) -> str:
        """URL of API for objects of that class.

            Used in `cls.get_api` property.

            Returns
            -------
            str
                API URL.
            """
        ...

    @classmethod
    def from_dict(cls: Type[element], new_instance: dict[str, Any]) -> element:
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
    def get(cls, *, method_: str = "all", **attr_to_value: Union[Any, Iterable[Any]]) -> ElementGroup[element]:
        """Gets a group of elements based on filters and conditions passed.

        Conditions passed by `attr_to_value`. E.g. `web_name="Spurs"`

        Parameters
        ----------
        method_ : str, optional
            "all" if all conditions must be met, "or" for any condition to be met, by default "all"

        Returns
        -------
        ElementGroup[element]
            All elements that satisfy the filters passed, may also be empty.
        """
        all_elems = cls.get_all()

        return all_elems.filter(method_=method_, **attr_to_value)

    @classmethod
    @cache
    def get_all(cls) -> ElementGroup[element]:
        """Gets all elements as objects of parent class `Element`.

        Returns
        -------
        ElementGroup[element]
            All elements.
        """
        elements = cls.get_api()
        elements_sorted = sorted([cls.from_dict(elem) for elem in elements], key=lambda p: p.unique_id)

        return ElementGroup[element](elements_sorted)

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
        if (refresh_api is True) or (cls._api is None):  # If api is empty or an update to api is requested.
            cls._api = cls.get_latest_api()

        return cls._api

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
        """
        filter_ = {cls.UNIQUE_ID_COL: id_}
        element_group = cls.get(**filter_)

        try:
            id_uniqueness_check(element_group)
        except IDMatchesZeroElements:
            return None
        else:
            return element_group[0]

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
        ...


class ElementGroup2(ABC, list[element], Generic[element]):
    def __init__(self, objects: Iterable[element]):
        super().__init__(*objects)

    def to_df(self, *attributes: str) -> pd.DataFrame:
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

    def to_percentile(self, attr: str) -> Percentile[element]:
        """Ranks all elements in instance by percentile by `attr`.

        Parameters
        ----------
        attr : str
            Attribute to rank elements by.

        Returns
        -------
        Percentile[element]
           Gives each element a rank.

        Raises
        ------
        TypeError
            Attribute type must be int or float.
        """
        elements_to_attr = {elem: getattr(elem, attr) for elem in self}

        for attr_value in elements_to_attr.values():
            if not isinstance(attr_value, (int, float)):
                raise TypeError("Must be int or float.")

        return Percentile[element](elements_to_attr)

    def to_string_list(self) -> list[str]:
        """All elements in instance as their string representation.

        Returns
        -------
        list[str]
            All elements in instance as their string representation.
        """
        output = [str(elem) for elem in self]

        return output


class ElementGroup(ABC, Generic[element]):
    """Way to store and edit a group of common FPL elements.
    """

    def __init__(self, objects: Iterable[element]):
        # Need to find a method of removing duplicates whilst preserving order.
        self.__objects = list(objects)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ElementGroup):
            raise NotImplementedError

        return other.to_list() == self.to_list()

    def __add__(self, other: ElementGroup[element]) -> ElementGroup[element]:
        if not isinstance(other, ElementGroup):
            raise NotImplementedError

        if not self.is_compatible(other):
            raise Exception("ElementGroups must have same type.")

        return ElementGroup[element](self.to_list() + other.to_list())

    @overload
    def __getitem__(self, idx: SupportsIndex) -> element: ...
    @overload
    def __getitem__(self, idx: slice) -> ElementGroup[element]: ...

    def __getitem__(self, idx: Any) -> Any:
        if isinstance(idx, slice):
            # slicing creates new ElementGroup
            return ElementGroup(self.__objects[idx])
        elif isinstance(idx, SupportsIndex):
            return self.__objects[idx]
        else:
            raise NotImplementedError

    def __iter__(self) -> Iterator[element]:
        return iter(self.__objects)

    def __len__(self) -> int:
        return len(self.__objects)

    def __str__(self) -> str:
        """Description of contents in the class.

        Returns
        -------
        str
            E.g. 'ElementGroup of 10 elements.'
        """
        return f"{self.__class__.__name__} of {len(self)} elements."

    def filter(self, *, method_: str = "all", **attr_to_value: Union[Any, tuple[Any]]) -> ElementGroup[element]:
        """Filters an ElementGroup into a group that satisfies all the conditions passed.

        Parameters
        ----------
        method_ : bool, optional
            "all" if all conditions must be met, "or" for any condition to be met, by default "all"

        Returns
        -------
        ElementGroup[element]
            All elements that satisfy the filters.

        Raises
        ------
        AttributeError
            If the attribute does not exist for the elements.
        """
        # Method check
        func = _method_choice(method_)
        attr_to_value = _format_attr_to_value(attr_to_value)

        elements_found = []

        for elem in self:
            conditions_by_attr = []

            for attr, values in attr_to_value.items():
                elem_attr = getattr(elem, attr)

                if isinstance(elem_attr, _Element):
                    elem_attr = elem_attr.unique_id

                for value in values:
                    if elem_attr == value:
                        conditions_by_attr.append(True)
                        break
                else:
                    conditions_by_attr.append(False)

            if func(conditions_by_attr):
                elements_found.append(elem)

        return ElementGroup[element](elements_found)

    def get_top_n_elements(self, col_by: str, n: int, reverse: bool = True) -> ElementGroup[element]:
        """Gets top n elements of an attribute and returns them in a new ElementGroup.

        Parameters
        ----------
        col_by : str
            Attribute to rank elements by.
        n : int
            Number of elements to save.
        reverse : bool, optional
           For descending order, use True, by default True

        Returns
        -------
        ElementGroup[element]
            Group of top elements of size `n`.
        """
        return ElementGroup[element](self.sort(col_by, reverse=reverse)[:n])

    def get_random(self) -> element:
        """Gets random element from objects list.

        Returns
        -------
        element
            Random element selected.
        """
        return choice(self.__objects)

    def get_sample(self, n: int) -> ElementGroup[element]:
        """Gets `n` random elements from `self`.

        Parameters
        ----------
        n : int
            Length of new element group.

        Returns
        -------
        ElementGroup[element]
            `n` elements from random sample.
        """
        return ElementGroup[element](list(sample(self.__objects, n)))

    def group_by(self, group_by_attr: str) -> dict[Any, ElementGroup[element]]:
        """Split an ElementGroup into multiple sub-groups by an attribute value.

        Parameters
        ----------
        group_by_attr : str
            Attribute to create groups by.

        Returns
        -------
        dict[Any, ElementGroup[element]]
            The key is the attribute value, the value is elements with a common attribute value.

        Raises
        ------
        AttributeError
            If `group_by_attr` does not exist for the elements.
        """
        groups: dict[Any, list[element]]
        groups = {}

        for elem in self:
            elem_attr = getattr(elem, group_by_attr, None)

            if elem_attr is None:
                raise AttributeError(
                    f"'{group_by_attr}' not in attributes.")

            if elem_attr not in groups:
                groups[elem_attr] = [elem]  # Creates new group
            else:
                groups[elem_attr].append(elem)

        return {attr: ElementGroup[element](elems) for attr, elems in groups.items()}

    def is_compatible(self, other: ElementGroup[Any]) -> bool:
        """Checks if two ElementGroups store the same element.

        Parameters
        ----------
        other : ElementGroup
            Other group of elements to compare against.

        Returns
        -------
        bool
            True if they both store the same elements, False otherwise.
        """
        subtypes_found = []

        full_list = self.to_list() + other.to_list()

        for elem in full_list:
            if type(elem) not in subtypes_found:
                subtypes_found.append(type(elem))

                if len(subtypes_found) > 1:
                    return False

        return True

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

        def foo(elem: _Element[Any]) -> Any:
            return getattr(elem, sort_by)

        if self.__objects == []:
            return ElementGroup[element](self.__objects)

        elements_sorted = sorted(self.__objects, key=foo, reverse=reverse)

        return ElementGroup[element](elements_sorted)

    def split(self, *, method_: str = "all", **attr_to_value: Union[Any, Iterable[Any]]) -> tuple[ElementGroup[element], ElementGroup[element]]:
        """Splits an ElementGroup into two sub-groups, where one group satisfies the filters, the other does not.

        Parameters
        ----------
        method_ : bool, optional
            "all" if all conditions must be met, "or" for any condition to be met, by default "all"

        Returns
        -------
        tuple[ElementGroup[element], ElementGroup[element]]
            The first group satisfies the filter, the other does not.
        """
        filtered_elems = self.filter(method_=method_, **attr_to_value)

        not_filtered_elems = ElementGroup[element](
            [elem for elem in self if elem not in filtered_elems.to_list()])

        return filtered_elems, not_filtered_elems

    def to_df(self, *attributes: str) -> pd.DataFrame:
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

    def to_list(self) -> list[element]:
        """All elements in instance within a list.

        Returns
        -------
        list[element]
            `self.__object`.
        """
        return self.__objects

    def to_percentile(self, attr: str) -> Percentile[element]:
        """Ranks all elements in instance by percentile by `attr`.

        Parameters
        ----------
        attr : str
            Attribute to rank elements by.

        Returns
        -------
        Percentile[element]
           Gives each element a rank.

        Raises
        ------
        TypeError
            Attribute type must be int or float.
        """
        elements_to_attr = {elem: getattr(elem, attr) for elem in self}

        for attr_value in elements_to_attr.values():
            if not isinstance(attr_value, (int, float)):
                raise TypeError("Must be int or float.")

        return Percentile[element](elements_to_attr)

    def to_string_list(self) -> list[str]:
        """All elements in instance as their string representation.

        Returns
        -------
        list[str]
            All elements in instance as their string representation.
        """
        output = [str(elem) for elem in self]

        return output


class InvalidQueryResult(Exception):
    pass


class IDNotUnique(InvalidQueryResult):
    pass


class IDMatchesZeroElements(InvalidQueryResult):
    pass


def id_uniqueness_check(query_result_from_id: ElementGroup[Any]) -> None:
    """Checks if result from ID search produces a valid result.

    Parameters
    ----------
    query_result_from_id : ElementGroup[Any]
        Result from searching for an item by its ID, usually using `cls.get_by_id()`.

    Raises
    ------
    IDNotUnique
        If the query result has more than 1 element.
    IDMatchesZeroElements
        If the query result has 0 elements.
    InvalidQueryResult
        The query result does not have a length of 1.
    """
    if len(query_result_from_id) == 1:
        return

    if len(query_result_from_id) > 1:
        raise IDNotUnique(
            f"Expected only one element, got {len(query_result_from_id)}.")
    if len(query_result_from_id) == 0:
        raise IDMatchesZeroElements("ID matches 0 elements.")


def _method_choice(method_: str) -> Callable[[Iterable[bool]], bool]:
    """Checks if method choice passed from `get` is acceptable.

    Parameters
    ----------
    method_ : str
        Choice of applying conditions. E.g. `all()`,  `any()`.

    Returns
    -------
    Callable[[Iterable[bool]], bool]
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


def _format_attr_to_value(attr_to_value: dict[str, Union[Any, tuple[Any, ...]]]) -> dict[str, tuple[Any, ...]]:
    """Formats query so the values are all tuples.

    Used by `ElementGroup.filter()`

    Parameters
    ----------
    attr_to_value : dict[str, Union[Any, tuple[Any]]]
        Original query

    Returns
    -------
    dict[str, tuple[Any]]
        Formatted query where values are stored in tuples by default.
    """
    # Attr_to_value check
    for attr, values in attr_to_value.items():
        # If single value for attr is passed
        if isinstance(values, tuple):
            attr_to_value[attr] = list(values)
        else:
            attr_to_value[attr] = [values]

    no_elem_attr_to_value: dict[str, tuple[Any, ...]] = dict()

    for attr, values in attr_to_value.items():
        temp: list[Any] = []

        for value in values:
            if isinstance(value, _Element):
                temp.append(value.unique_id)
            else:
                temp.append(value)

        no_elem_attr_to_value[attr] = tuple(temp)

    return no_elem_attr_to_value


'''def elem_from_dict(elem_class: type[_Element], new_instance: dict[str, Any]) -> element:
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
        f"Missing: {field_names.difference(set(new_instance.keys()))}")'''

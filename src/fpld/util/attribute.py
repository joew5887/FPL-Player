from dataclasses import fields
from typing import Any, Generic, Iterator, Sequence, TypeVar, Union, List
from .percent import to_percent
from ..constants import round_value


t = TypeVar("t")  # Attribute value
_b = TypeVar("_b", int, float)  # Continuous attribute value type
_KT = TypeVar("_KT")  # label for Percentile


class Percentile(Generic[_KT]):
    """For a list of named labels and their values, show the labels arranged by percentile.

    The higher the value, the higher the rank and percentile.
    """
    __name_to_value: dict[_KT, Union[int, float]]
    __name_to_percentile: dict[_KT, int]
    __name_to_rank: dict[_KT, int]
    __rank_to_name: list[_KT]

    def __init__(self, name_to_value: dict[_KT, Union[int, float]]):
        self.__set_name_to_value(name_to_value)

    def __str__(self) -> str:
        """Show minimum and maximum values for Percentile object.

        Returns
        -------
        str
            Shows key at the minimum and maximum values as well as their values.

        Example
        -------
        ```
        > percentile = Percentile({"1": 0.0, "2": 0.5, "3": 0.75, "4": 1})
        > str(percentile)
        "Percentile(min_key=1, min_value=0, MAX_key=4, MAX_value=1)"
        ```
        """
        output = []
        min_key = self.name_at_rank(0)
        max_key = self.name_at_rank(self.max_rank)
        output.append(f"min_key={min_key}")
        output.append(f"min_value={self.get_value(min_key)}")
        output.append(f"MAX_key={max_key}")
        output.append(f"MAX_value={self.get_value(max_key)}")
        output.append(f"__len__={len(self)}")

        content = ", ".join(output)
        return f"Percentile({content})"

    def __len__(self) -> int:
        """Number of elements in Percentile object.

        Returns
        -------
        int
            Minimum of 1.
        """
        return len(self.__name_to_value)

    @property
    def max_rank(self) -> int:
        """Shows the highest rank for Percentile object.

        Returns
        -------
        int
            ```len(self) - 1```. Minimum of 0.
        """
        return len(self) - 1

    def __set_name_to_value(self, new_name_to_value: dict[_KT, Union[int, float]]) -> None:
        if len(new_name_to_value) <= 1:
            raise Exception("Must be more than 1 element to compare.")

        self.__name_to_value = new_name_to_value
        # self.__values = list(self.__name_to_value.values())
        self.__update_ranks()
        self.__update_name_to_percentile()

    def __update_ranks(self) -> None:
        sorted_by_value = sorted(
            self.__name_to_value, key=lambda p: self.__name_to_value[p]
        )
        self.__name_to_rank = {key: i for i, key in enumerate(sorted_by_value)}
        self.__rank_to_name = sorted_by_value

    def __update_name_to_percentile(self) -> None:
        self.__name_to_percentile = {key: int(to_percent(rank, len(self))) for key, rank in self.__name_to_rank.items()
                                     }

    '''def append(self, name, value) -> None:
        new_name_to_value = {**self.__name_to_value, **{name: value}}
        self.name_to_value = new_name_to_value

    def remove(self, name) -> None:
        del self.name_to_value[name]'''

    def get_rank(self, key: _KT) -> int:
        """Get the rank for a key, if it exists in the Percentile object.

        Parameters
        ----------
        key : _KT
            Key to search rank for.

        Returns
        -------
        int
            Rank found.

        Examples
        ------
        ```
        > percentile = Percentile({"1": 0.0, "2": 0.5, "3": 0.75, "4": 1})
        > percentile.get_rank("1")
        0
        > percentile.get_rank("2")
        1
        > percentile.get_rank("3")
        2
        > percentile.get_rank("4")
        3
        """
        return self.__name_to_rank[key]

    def get_percentile(self, key: _KT) -> int:
        """Get percentile for a key, if it exists in the Percentile object.

        Parameters
        ----------
        key : _KT
            Key to search percentile for.

        Returns
        -------
        int
            Percentage as integer. Lower bound percentile value.

        Examples
        ------
        ```
        > percentile = Percentile({"1": 0.0, "2": 0.5, "3": 0.75, "4": 1})
        > percentile.get_percentile("1")
        0
        > percentile.get_percentile("2")
        25
        > percentile.get_percentile("3")
        50
        > percentile.get_percentile("4")
        75
        """
        return self.__name_to_percentile[key]

    def get_value(self, key: _KT) -> Union[int, float]:
        """Get value for a key, if it exists in the Percentile object.

        Parameters
        ----------
        key : _KT
            Key to search value for.

        Returns
        -------
        Union[int, float]
            Value for the key.

        Examples
        ------
        ```
        > percentile = Percentile({"1": 0.0, "2": 0.5, "3": 0.75, "4": 1})
        > percentile.get_value("1")
        0.0
        > percentile.get_value("2")
        0.5
        """
        return self.__name_to_value[key]

    def name_at_rank(self, rank: int) -> _KT:
        """Get key label at rank.

        Parameters
        ----------
        rank : int
            Rank to find key for.

        Returns
        -------
        _KT
            Key at rank passed.

        Raises
        ------
        IndexError
            If rank is not within the range of elements in Percentile object.
        """
        try:
            name = self.__rank_to_name[rank]
        except IndexError:
            rank_range = f"Rank goes from 0-{self.max_rank}"
            raise IndexError(f"{rank_range}. Rank passed was '{rank}'.")
        else:
            return name

    '''def x_axis_data(self) -> list[Union[int, float]]:
        ub = int(max(self.__values) + 1)
        lb = int(min(self.__values) - 1)

        return list(range(lb, ub))

    def y_axis_data(self) -> list[int]:
        x = self.x_axis_data()
        y = [0 for _ in range(len(x))]

        for value in self.__values:
            for i in range(len(x)-1):
                if x[i] <= value and value < x[i+1]:
                    y[i] += 1

        return y

    def graph_axes(self) -> tuple[list[Union[int, float]], list[int]]:
        x = self.x_axis_data()
        y = self.y_axis_data()

        return x, y'''


class Attribute(Generic[t]):
    """Stores values related to an attribute by its name.
    """

    def __init__(self, values: Sequence[t], attr_name: str):
        self.values = list(values)
        self.__attr_name = attr_name

    def __str__(self) -> str:
        """Show attribute name and values present.

        Returns
        -------
        str
            Shows attribute name and values, separated by colon.

        Example
        -------
        ```
        > attribute = Attribute([1, 2, 3, 4, 5], "foo")
        > str(attribute)
        "foo - [1, 2, 3, 4, 5]"
        """
        return f"{self.__attr_name} - {self.__values}"

    def __len__(self) -> int:
        """Number of values in Attribute object.

        Returns
        -------
        int
            Length of `self.values`.
        """
        return len(self.values)

    def __iter__(self) -> Iterator[t]:
        return iter(self.values)

    @property
    def values(self) -> list[t]:
        """Values stored under attribute name.

        Returns
        -------
        list[t]
            Unordered list of values.
        """
        return self.__values

    @values.setter
    def values(self, new_values: List[t]) -> None:
        if len(new_values) == 0:  # Empty list check.
            raise Exception("Empty list passed!")

        self.__values = new_values
        # self.__edit_values()

    '''def __edit_values(self) -> None:
        pass'''


class CategoricalVar(Attribute[t]):
    """For attributes with categorical data values.
    """

    def __init__(self, values: Sequence[t], attr_name: str):
        super().__init__(values, attr_name)


class ContinuousVar(Attribute[_b]):
    """For attributes with continuous data values.
    """

    def __init__(self, values: Sequence[_b], attr_name: str):
        super().__init__(values, attr_name)

    '''def __edit_values(self) -> None:
        super().__edit_values()'''

    @property
    def average(self) -> float:
        """Average value of all values in object.

        Returns
        -------
        float
            Total of all values divided by number of values.
        """
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

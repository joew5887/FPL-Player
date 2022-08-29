from dataclasses import fields
from typing import Any, Generic, Iterator, TypeVar, Union
from datetime import datetime


t = TypeVar("t")
b = TypeVar("b", int, float)
_KT = TypeVar("_KT")


class Percentile(Generic[_KT]):
    def __init__(self, name_to_value: dict[_KT, Union[float, int]]):
        self.__set_name_to_value(name_to_value)

    def __str__(self) -> str:
        output = []
        min_key = self.name_at_rank(0)
        max_key = self.name_at_rank(self.max_rank)
        output.append(f"Min key = {min_key}")
        output.append(f"Min value = {self.get_value(min_key)}")
        output.append(f"Max key = {max_key}")
        output.append(f"Max value = {self.get_value(max_key)}")
        output.append(f"Number of elements = {len(self)}")

        return "\n".join(output)

    def __len__(self) -> int:
        return len(self.__name_to_value)

    @property
    def max_rank(self) -> int:
        return len(self) - 1

    def __set_name_to_value(self, new_name_to_value: dict[Any, Union[int, float]]) -> None:
        self.__name_to_value = new_name_to_value
        self.__values = list(self.__name_to_value.values())
        self.__update_ranks()
        self.__update_name_to_percentile()

    def __update_ranks(self) -> None:
        sorted_by_value = sorted(
            self.__name_to_value, key=self.__name_to_value.get
        )
        self.__name_to_rank = {key: i for i, key in enumerate(sorted_by_value)}
        self.__rank_to_name = sorted_by_value

    def __update_name_to_percentile(self) -> None:
        self.__name_to_percentile = {key: self.__formula(
            rank) for key, rank in self.__name_to_rank.items()
        }

    def append(self, name, value) -> None:
        new_name_to_value = {**self.__name_to_value, **{name: value}}
        self.name_to_value = new_name_to_value

    def remove(self, name) -> None:
        del self.name_to_value[name]

    def get_rank(self, key: Any) -> int:
        return Percentile.__get_value(key, self.__name_to_rank)

    def get_percentile(self, key: Any) -> int:
        return Percentile.__get_value(key, self.__name_to_percentile)

    def get_value(self, key: Any) -> int:
        return Percentile.__get_value(key, self.__name_to_value)

    def name_at_rank(self, rank: int) -> _KT:
        try:
            name = self.__rank_to_name[rank]

        except IndexError:
            rank_range = f"Rank goes from 0-{self.max_rank}"
            raise IndexError(f"{rank_range}. Rank passed was '{rank}'.")

        else:
            return name

    def __formula(self, rank: int) -> int:
        percentile = (rank / len(self)) * 100

        return round(percentile)

    def x_axis_data(self) -> list:
        ub = int(max(self.__values) + 1)
        lb = int(min(self.__values) - 1)

        return list(range(lb, ub))

    def y_axis_data(self) -> list:
        x = self.x_axis_data()
        y = [0] * len(x)

        for value in self.__values:
            for i in range(len(x)-1):
                if x[i] <= value and value < x[i+1]:
                    y[i] += 1

        return y

    def graph_axes(self) -> tuple:
        x = self.x_axis_data()
        y = self.y_axis_data()

        return x, y

    @staticmethod
    def __get_value(key: Any, name_to_value: dict) -> _KT:
        try:
            value = name_to_value[key]
        except KeyError:
            raise KeyError(f"'{key}' not in names.")
        else:
            return value


class Attribute(Generic[t]):
    def __init__(self, values: list[t], attr_name: str):
        self.values = values
        self.__attr_name = attr_name

    def __str__(self) -> str:
        return f"{self.__attr_name} - {self.__values}"

    def __iter__(self) -> Iterator[t]:
        return iter(self.values)

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


def string_date(date_: datetime) -> str:
    return date_.strftime("%a %d %B %Y")


def string_time(date_: datetime) -> str:
    return date_.strftime("%H:%M")


def string_datetime(date_: datetime):
    return string_time(date_) + " - " + string_date(date_)

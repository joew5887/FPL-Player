# import fpld
from typing import Any
import pytest
from fpld.util.attribute import ContinuousVar, Percentile, Attribute, CategoricalVar


VALID_PERCENTILE = Percentile[str]({
    "1": 0.1,  "2": 0.2, "3": 0.3, "4": 0.4, "5": 0.5,
    "6": 0.6, "7": 0.7, "8": 0.8, "9": 0.9, "10": 1
})

VALID_ATTRIBUTE = Attribute[int]([1, 2, 3, 4, 5], "foo")
VALID_CONTINUOUS_ATTRIBUTE = ContinuousVar[int]([1, 2, 3, 4, 5], "foo")
VALID_CATEGORICAL_ATTRIBUTE = CategoricalVar[int](["yes", "no"], "bar")


class TestPercentileExample:
    percentile = VALID_PERCENTILE
    expected: dict[str, Any] = {
        "__str__": "Percentile(min_key=1, min_value=0.1, MAX_key=10, MAX_value=1, __len__=10)",
        "__len__": 10,
        "max_rank": 9,
        "get_rank": ("1", 0),
        "get_percentile": ("3", 20),
        "get_value": ("7", 0.7),
        "name_at_rank": (9, "10"),
    }

    def test_str(self) -> None:
        assert str(self.percentile) == self.expected["__str__"]

    def test_len(self) -> None:
        assert len(self.percentile) == self.expected["__len__"]

    def test_max_rank(self) -> None:
        assert self.percentile.max_rank == self.expected["max_rank"]

    def test_get_rank(self) -> None:
        name: str
        expected_rank: int
        name, expected_rank = self.expected["get_rank"]

        assert self.percentile.get_rank(name) == expected_rank

    def test_get_percentile(self) -> None:
        name: str
        expected_percentile: int
        name, expected_percentile = self.expected["get_percentile"]

        assert self.percentile.get_percentile(name) == expected_percentile

    def test_get_value(self) -> None:
        name: str
        expected_value: int
        name, expected_value = self.expected["get_value"]

        assert self.percentile.get_value(name) == expected_value

    def test_name_at_rank(self) -> None:
        rank: int
        expected_name: str
        rank, expected_name = self.expected["name_at_rank"]

        assert self.percentile.name_at_rank(rank) == expected_name


class TestPercentileCases:
    percentile = VALID_PERCENTILE

    def test_empty_input(self) -> None:
        with pytest.raises(Exception):
            Percentile({})

    def test_input_of_2(self) -> None:
        percentile = Percentile({"1": 0, "2": 1})

        assert percentile.max_rank == 1

    def test_invalid_key(self) -> None:
        with pytest.raises(KeyError):
            self.percentile.get_rank("foo")
            self.percentile.get_percentile("foo")
            self.percentile.get_value("foo")

    def test_invalid_rank(self) -> None:
        with pytest.raises(IndexError):
            self.percentile.name_at_rank(11)


class TestAttributeExample:
    attribute = VALID_ATTRIBUTE
    expected: dict[str, Any] = {
        "__str__": "foo - [1, 2, 3, 4, 5]",
        "__len__": 5,
        "__iter__": [1, 2, 3, 4, 5],
        "values": [1, 2, 3, 4, 5]

    }

    def test_str(self) -> None:
        assert str(self.attribute) == self.expected["__str__"]

    def test_len(self) -> None:
        assert len(self.attribute) == self.expected["__len__"]

    def test_iter(self) -> None:
        assert [x for x in self.attribute] == self.expected["__iter__"]

    def test_values(self) -> None:
        assert self.attribute.values == self.expected["values"]


class TestCategoricalVarExample:
    attribute = VALID_CATEGORICAL_ATTRIBUTE

    expected: dict[str, Any] = {
        "__str__": "bar - ['yes', 'no']",
        "__len__": 2,
        "__iter__": ["yes", "no"],
        "values": ["yes", "no"]

    }


class TestContinuousVarExample:
    attribute = VALID_CONTINUOUS_ATTRIBUTE

    continuous_expected: dict[str, Any] = {
        "average": 3.0
    }

    def test_average(self) -> None:
        assert self.attribute.average == self.continuous_expected["average"]


class TestAttributeCases:
    def test_empty_input(self) -> None:
        with pytest.raises(Exception):
            Attribute[int]([], "foo")


if __name__ == "__main__":
    pytest.main([__file__])

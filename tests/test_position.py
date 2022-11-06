import pytest
from typing import Union, Any
from .test_elements import Element, ElementClass
from fpld.elements.fplelems import Position
from fpld.elements.element import IDMatchesZeroElements


class TestPositionExample(Element[Position]):
    element_to_test: Position = Position.get_by_id(4)
    expected: dict[str, Any] = {
        "__str__": "Forward",
        "__repr__": "Position(singular_name='Forward')",
        "unique_id": 4,
    }


class TestPositionClass(ElementClass[Position]):
    class_to_test = Position
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
        "get_all_dict": {
            "GKP": Position.get_by_id(1), "DEF": Position.get_by_id(2),
            "MID": Position.get_by_id(3), "FWD": Position.get_by_id(4)
        }
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (1, Position.get(singular_name_short="GKP")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[Position, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    @pytest.mark.parametrize("singular_name_short,expected_id", [("GKP", 1), ("DEF", 2), ("MID", 3), ("FWD", 4)])
    def test_get_by_name(self, singular_name_short:  str, expected_id: int) -> None:
        assert self.class_to_test.get_by_name(singular_name_short).unique_id == expected_id

    def test_invalid_get_by_name(self) -> None:
        with pytest.raises(IDMatchesZeroElements):
            self.class_to_test.get_by_name("FOO")

    def test_get_all_dict(self) -> None:
        assert self.class_to_test.get_all_dict() == self.expected["get_all_dict"]

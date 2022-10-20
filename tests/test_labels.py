import pytest
from typing import Union, Any
from .test_elements import Element, ElementClass
from fpld.elements.fplelems import Label


class TestLabelExample(Element[Label]):
    element_to_test: Label = Label.get_by_id("goals_scored")
    expected: dict[str, Any] = {
        "__str__": "Goals scored",
        "__repr__": "Label(label='Goals scored', name='goals_scored')",
        "unique_id": "goals_scored",
    }


class TestLabelClass(ElementClass[Label]):
    class_to_test = Label
    expected: dict[str, Any] = {
        "unique_id_col": "name",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 ("assists", Label.get(label="Assists")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[Label, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

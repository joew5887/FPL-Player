import pytest
from typing import Union, Any
from .test_elements import Element, ElementClass
from fpld.elements.fplelems import Team


class TestTeamExample(Element[Team]):
    element_to_test: Team = Team.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "Arsenal",
        "__repr__": "Team(name='Arsenal')",
        "unique_id": 1,
    }


class TestTeamClass(ElementClass[Team]):
    class_to_test = Team
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (1, Team.get(name="Arsenal")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[Team, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    def test_get_all_names(self) -> None:
        output = self.class_to_test.get_all_names()

        assert len(output) == 20 and output[0] == "Arsenal"

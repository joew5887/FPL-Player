from abc import ABC
import pytest
from fpld import elements as elems
from fpld.elements.element import IDMatchesZeroElements
from fpld.util import Percentile
from typing import Any, Callable, SupportsIndex, TypeVar, Generic, Union
import pandas as pd


if __name__ == "__main__":
    from examples import PLAYERS, TEAM_DF
else:
    from .examples import PLAYERS, TEAM_DF


_element = TypeVar("_element", bound=elems.element._Element)


class Element(ABC, Generic[_element]):
    expected: dict[str, Any] = {
        "__str__": "",
        "__repr__": "",
        "unique_id": 0
    }

    @property
    def element_to_test(self) -> _element:
        raise NotImplementedError

    def test_str(self) -> None:
        assert str(self.element_to_test) == self.expected["__str__"]

    def test_repr(self) -> None:
        assert repr(self.element_to_test) == self.expected["__repr__"]

    def test_info(self) -> None:
        info = self.element_to_test.info

        assert isinstance(info, str)

    def test_unique_id(self) -> None:
        id_found = self.element_to_test.unique_id

        assert id_found == self.expected["unique_id"]


class TestPlayerExample(Element[elems.Player]):
    element_to_test: elems.Player = elems.Player.get_by_id(427)
    expected: dict[str, Any] = {
        "__str__": "Kane",
        "__repr__": "Player(element_type=Position(singular_name='Forward'), team=Team(name='Spurs'), web_name='Kane')",
        "unique_id": 427,
    }


class TestPositionExample(Element[elems.Position]):
    element_to_test: elems.Position = elems.Position.get_by_id(4)
    expected: dict[str, Any] = {
        "__str__": "Forward",
        "__repr__": "Position(singular_name='Forward')",
        "unique_id": 4,
    }


class TestLabelExample(Element[elems.Label]):
    element_to_test: elems.Label = elems.Label.get_by_id("goals_scored")
    expected: dict[str, Any] = {
        "__str__": "Goals scored",
        "__repr__": "Label(label='Goals scored', name='goals_scored')",
        "unique_id": "goals_scored",
    }


class TestTeamExample(Element[elems.Team]):
    element_to_test: elems.Team = elems.Team.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "Arsenal",
        "__repr__": "Team(name='Arsenal')",
        "unique_id": 1,
    }


class TestEventExample(Element[elems.Label]):
    element_to_test: elems.Event = elems.Event.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "Gameweek 1",
        "__repr__": "Event(name='Gameweek 1')",
        "unique_id": 1,
        "started": True,
    }

    def test_started(self) -> None:
        assert self.element_to_test.started == self.expected["started"]


class TestFixtureExample(Element[elems.Fixture]):
    element_to_test: elems.Fixture = elems.Fixture.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "Crystal Palace v Arsenal",
        "__repr__": "Fixture(event=Event(name='Gameweek 1'), team_a=Team(name='Arsenal'), team_h=Team(name='Crystal Palace'))",
        "unique_id": 1,
        "score": "(Crystal Palace) 0 - 2 (Arsenal)",
        "total_goals": 2,
    }

    def test_score(self) -> None:
        assert self.element_to_test.score == self.expected["score"]

    def test_total_goals(self) -> None:
        assert self.element_to_test.total_goals == self.expected["total_goals"]


class TestFixtureFutureExample(TestFixtureExample):
    element_to_test: elems.Fixture = elems.Fixture.get_by_id(380)
    expected: dict[str, Any] = {
        "__str__": "Southampton v Liverpool",
        "__repr__": "Fixture(event=Event(name='Gameweek 38'), team_a=Team(name='Liverpool'), team_h=Team(name='Southampton'))",
        "unique_id": 380,
        "score": "Southampton v Liverpool",
        "total_goals": None,
    }


class ElementClass(ABC, Generic[_element]):
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
    }

    @property
    def class_to_test(self) -> _element:
        raise NotImplementedError

    def test_api_link(self) -> None:
        api_link = self.class_to_test.api_link

        assert api_link == self.expected["api_link"]

    def test_unique_id_col(self) -> None:
        unique_id_col = self.class_to_test.UNIQUE_ID_COL

        assert unique_id_col == self.expected["unique_id_col"]

    def test_incorrect_attributes_from_dict(self) -> None:
        invalid_input = {"not_existing_attr": 0}

        with pytest.raises(KeyError):
            self.class_to_test.from_dict(invalid_input)

    # get
    # get_all

    def test_get_api(self) -> None:
        api = self.class_to_test.get_api()

        assert isinstance(api, list)
        assert id(api) == id(self.class_to_test._api)

        api_2 = self.class_to_test.get_api()

        assert id(api) == id(api_2)

        api_3 = self.class_to_test.get_api(True)

        assert id(api) != id(api_3)

    def test_get_by_id(self, id_input: int, expected_output: Union[_element, None]) -> None:
        assert self.class_to_test.get_by_id(id_input) == expected_output


class TestPlayerClass(ElementClass[elems.Player]):
    class_to_test = elems.Player
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/"
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (427, elems.Player.get(web_name="Kane")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[_element, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)


class TestPositionClass(ElementClass[elems.Position]):
    class_to_test = elems.Position
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
        "get_all_dict": {
            "GKP": elems.Position.get_by_id(1), "DEF": elems.Position.get_by_id(2),
            "MID": elems.Position.get_by_id(3), "FWD": elems.Position.get_by_id(4)
        }
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (1, elems.Position.get(singular_name_short="GKP")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[_element, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    @pytest.mark.parametrize("singular_name_short,expected_id", [("GKP", 1), ("DEF", 2), ("MID", 3), ("FWD", 4)])
    def test_get_by_name(self, singular_name_short:  str, expected_id: int) -> None:
        assert self.class_to_test.get_by_name(singular_name_short).unique_id == expected_id

    def test_invalid_get_by_name(self) -> None:
        with pytest.raises(IDMatchesZeroElements):
            self.class_to_test.get_by_name("FOO")

    def test_get_all_dict(self) -> None:
        assert self.class_to_test.get_all_dict() == self.expected["get_all_dict"]


class TestLabelClass(ElementClass[elems.Label]):
    class_to_test = elems.Label
    expected: dict[str, Any] = {
        "unique_id_col": "name",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 ("assists", elems.Label.get(label="Assists")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[_element, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)


class TestTeamClass(ElementClass[elems.Team]):
    class_to_test = elems.Team
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/",
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (1, elems.Team.get(name="Arsenal")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[_element, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    def test_get_all_names(self) -> None:
        output = self.class_to_test.get_all_names()

        assert len(output) == 20 and output[0] == "Arsenal"


class TestElementGroupExampleEmpty:
    group_to_test: elems.ElementGroup[elems.Team] = elems.ElementGroup[elems.Team]([])
    expected: dict[str, Any] = {
        "__iter__": [],
        "__len__": 0,
        "__str__": "ElementGroup of 0 elements.",
        "to_df": {"params": ("name", "short_name"), "output": pd.DataFrame([], columns=["name", "short_name"])},
        "to_string_list": []
    }

    def test_iter(self) -> None:
        assert [t for t in self.group_to_test] == self.expected["__iter__"]

    def test_len(self) -> None:
        assert len(self.group_to_test) == self.expected["__len__"]

    def test_str(self) -> None:
        assert str(self.group_to_test) == self.expected["__str__"]

    def test_to_df(self) -> None:
        assert (self.group_to_test.to_df(*self.expected["to_df"]["params"]).equals(self.expected["to_df"]["output"]))

    def test_to_string_list(self) -> None:
        assert self.group_to_test.to_string_list() == self.expected["to_string_list"]


class TestElementGroupExample(TestElementGroupExampleEmpty):
    group_to_test: elems.ElementGroup[elems.Team] = elems.Team.get_all()
    expected: dict[str, Any] = {
        "__iter__": [t for t in group_to_test.to_list()],
        "__len__": 20,
        "__str__": "ElementGroup of 20 elements.",
        "to_df": {"params": ("name", "short_name"), "output": TEAM_DF},
        "to_string_list": list(TEAM_DF["name"])
    }


class TestElementGroupCases:
    @pytest.mark.parametrize("group1,group2,expected_output",
                             [
                                 (elems.Player.get(team=18), elems.Player.get(element_type=1), elems.Player.get(method_="or", team=18, element_type=1))
                             ]
                             )
    def test_add(
            self, group1: elems.ElementGroup[_element], group2: elems.ElementGroup[_element],
            expected_output: elems.ElementGroup[_element]) -> None:

        actual_output = group1 + group2

        assert set(actual_output.to_list()) == set(expected_output.to_list())

    @pytest.mark.parametrize("group1,group2",
                             [
                                 (elems.Player.get(team=18), elems.Fixture.get(event=1))
                             ]
                             )
    def test_add_not_compatible(
            self, group1: elems.ElementGroup[_element], group2: elems.ElementGroup[Any]) -> None:

        with pytest.raises(Exception):
            group1 + group2

    @pytest.mark.parametrize("group1,group2",
                             [
                                 (elems.Player.get(team=18), 5)
                             ]
                             )
    def test_add_incorrect_type(self, group1: elems.ElementGroup[_element], group2: Any) -> None:
        with pytest.raises(NotImplementedError):
            group1 + group2

    @pytest.mark.parametrize("group,idx,expected", [(elems.Player.get(web_name="Kane"), 0, elems.Player.get_by_id(427))])
    def test_getitem_supportsindex(self, group: elems.ElementGroup[_element], idx: SupportsIndex, expected: _element) -> None:
        assert group[idx] == expected

    @pytest.mark.parametrize("group,idx", [(elems.Player.get(web_name="Kane"), 1)])
    def test_getitem_outside_range(self, group: elems.ElementGroup[_element], idx: SupportsIndex) -> None:
        with pytest.raises(IndexError):
            group[idx]

    @pytest.mark.parametrize("group,idx,expected_len", [(elems.Player.get_all(), slice(10, 20, 1), 10)])
    def test_getitem_slice(self, group: elems.ElementGroup[_element], idx: slice, expected_len: int) -> None:
        new_group = group[idx]

        assert isinstance(new_group, elems.ElementGroup)
        assert len(new_group) == expected_len

    @pytest.mark.parametrize("group,idx", [(elems.Player.get(element_type=1), "foo")])
    def test_getitem_incorrect_type(self, group: elems.ElementGroup[_element], idx: Any) -> None:
        with pytest.raises(NotImplementedError):
            group[idx]

    @pytest.mark.parametrize("group,kwargs", [(elems.Team.get_all(), {"foo": 123})])
    def test_filter_invalid_attr(self, group: elems.ElementGroup[_element], kwargs: dict[str, Any]) -> None:
        with pytest.raises(AttributeError):
            group.filter(**kwargs)

    @pytest.mark.parametrize("group,expected_length,cols", [(elems.Team.get_all(), 20, ["unavailable"])])
    def test_to_df(self, group: elems.ElementGroup[_element], expected_length: int, cols: list[str]) -> None:
        df = group.to_df(*cols)

        assert len(df) == expected_length
        assert list(set(df.columns)) == list(set(cols))

    @pytest.mark.parametrize("group,cols", [(elems.Team.get_all(), ["foo"])])
    def test_to_df_incorrect_attr(self, group: elems.ElementGroup[_element], cols: list[str]) -> None:
        with pytest.raises(AttributeError):
            group.to_df(*cols)

    @pytest.mark.parametrize("group,attr", [(elems.Player.get(team=18), "goals_scored")])
    def test_percentile(self, group: elems.ElementGroup[_element], attr: str) -> None:
        assert isinstance(group.to_percentile(attr), Percentile)

    @pytest.mark.parametrize("group,attr", [(elems.Player.get(team=18), "web_name")])
    def test_to_percentile_incorrect_type(self, group: elems.ElementGroup[_element], attr: str) -> None:
        with pytest.raises(TypeError):
            group.to_percentile(attr)

    @pytest.mark.parametrize("group,expected", [(elems.Player.get(web_name="Kane"), ["Kane"]), (elems.ElementGroup([]), [])])
    def test_to_string_list(self, group: elems.ElementGroup[_element], expected: list[str]) -> None:
        assert group.to_string_list() == expected


class TestIDUniquenessCheck:
    def test_one_result(self) -> None:
        players = elems.Player.get(web_name="Kane")

        assert len(players) == 1
        elems.element.id_uniqueness_check(players)

    def test_zero_results(self) -> None:
        teams = elems.Team.get(short_name="123")

        assert len(teams) == 0
        with pytest.raises(elems.element.IDMatchesZeroElements):
            elems.element.id_uniqueness_check(teams)

    def test_multiple_results(self) -> None:
        fixtures = elems.Fixture.get(event=1)

        assert len(fixtures) > 1
        with pytest.raises(elems.element.IDNotUnique):
            elems.element.id_uniqueness_check(fixtures)


class TestMethodChoice:
    @ pytest.mark.parametrize("input,expected_return", [("all", all), ("or", any)])
    def test_in_choices(self, input: str, expected_return: Callable) -> None:
        output = elems.element._method_choice(input)

        assert id(output) == id(expected_return)

    def test_not_in_choices(self) -> None:
        with pytest.raises(Exception):
            elems.element._method_choice("foo")


if __name__ == "__main__":
    pytest.main([__file__])

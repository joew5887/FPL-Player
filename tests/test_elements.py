from abc import ABC
import pytest
from fpld import elements as elems
from fpld.util import Percentile
from typing import Any, Callable, SupportsIndex, TypeVar, Generic, Union


_element = TypeVar("_element", bound=elems.element._Element)


class Element(ABC, Generic[_element]):
    @property
    def element_to_test(self) -> _element:
        raise NotImplementedError

    @property
    def str_output(self) -> str:
        raise NotImplementedError

    @property
    def unique_id(self) -> str:
        raise NotImplementedError

    def test_str(self) -> None:
        assert str(self.element_to_test) == self.str_output

    def test_info(self) -> None:
        info = self.element_to_test.info

        assert isinstance(info, str)

    def test_unique_id(self) -> None:
        id_found = self.element_to_test.unique_id

        assert id_found == self.unique_id


class TestPlayer(Element[elems.Player]):
    element_to_test: elems.Player = elems.Player.get_by_id(427)
    str_output = "Kane"
    unique_id = 427


class TestSpurs(Element[elems.Team]):
    element_to_test: elems.Team = elems.Team.get_by_id(18)
    str_output = "Spurs"
    unique_id = 18


class ElementClass(Generic[_element]):
    @property
    def class_to_test(self) -> _element:
        raise NotImplementedError

    @property
    def unique_id_col(self) -> str:
        return "id"

    def test_api_link(self) -> None:
        api_link = self.class_to_test.api_link

        assert "http" in api_link

    def test_unique_id_col(self) -> None:
        unique_id_col = self.class_to_test.UNIQUE_ID_COL

        assert unique_id_col == self.unique_id_col

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

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (427, elems.Player.get(web_name="Kane")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[_element, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)


class TestElementGroup:
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

    def test_iter(self) -> None:
        group = elems.Player.get(element_type=1)

        assert all(e1 == e2 for e1, e2 in zip(group, group.to_list()))

    def test_len(self) -> None:
        group = elems.Team.get()

        assert len(group) == 20

    @pytest.mark.parametrize("group,expected", [(elems.Team.get_all(), "ElementGroup of 20 elements.")])
    def test_str(self, group: elems.ElementGroup[_element], expected: str) -> None:
        assert str(group) == expected

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

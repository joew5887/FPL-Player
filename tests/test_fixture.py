import pytest
from typing import Union, Any

from fpld.elements.element import ElementGroup
from .test_elements import Element, ElementClass
from fpld.elements.fplelems import Event, Fixture, Team
from fpld.elements.fixture import _fixture, BaseFixture


class FixtureElement(Element[_fixture]):
    expected: dict[str, Any] = {
        "__str__": "",
        "__repr__": "",
        "unique_id": 0,
        "score": "",
        "total_goals": 0,
    }


class TestBaseFixtureExample(FixtureElement[BaseFixture]):
    element_to_test: BaseFixture = BaseFixture.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "7 v 1",
        "__repr__": "BaseFixture(event=1, team_a=1, team_h=7)",
        "unique_id": 1,
        "score": "(7) 0 - 2 (1)",
        "total_goals": 2,
    }

    def test_score(self) -> None:
        assert self.element_to_test.score == self.expected["score"]

    def test_total_goals(self) -> None:
        assert self.element_to_test.total_goals == self.expected["total_goals"]


class TestFixtureExample(FixtureElement[Fixture]):
    element_to_test: Fixture = Fixture.get_by_id(1)
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
    element_to_test: Fixture = Fixture.get_by_id(380)
    expected: dict[str, Any] = {
        "__str__": "Southampton v Liverpool",
        "__repr__": "Fixture(event=Event(name='Gameweek 38'), team_a=Team(name='Liverpool'), team_h=Team(name='Southampton'))",
        "unique_id": 380,
        "score": "Southampton v Liverpool",
        "total_goals": None,
    }


class TestFixtureClass(ElementClass[Fixture]):
    class_to_test = Fixture
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/fixtures/"
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (1, Fixture.get(team_a=1, team_h=7)[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[Fixture, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    def test_get_all_team_fixtures(self) -> None:
        team = Team.get_by_id(1)
        all_fixtures = Fixture.get_all_team_fixtures(team.id)

        assert any(f.team_a == team or f.team_h != team for f in all_fixtures)

    @pytest.mark.parametrize("fixture_group,expected_output",
                             [
                                 (ElementGroup[Fixture]([Fixture.get_by_id(1), Fixture.get_by_id(380)]), {
                                  Event.get_by_id(1): ElementGroup[Fixture]([Fixture.get_by_id(1)]), Event.get_by_id(38): ElementGroup[Fixture]([Fixture.get_by_id(380)])}),
                             ]
                             )
    def test_group_fixtures_by_gameweek(self, fixture_group: ElementGroup[Fixture], expected_output: dict[Event, ElementGroup[Fixture]]) -> None:
        assert Fixture.group_fixtures_by_gameweek(fixture_group) == expected_output

    @pytest.mark.parametrize("fixture_group,expected_output",
                             [
                                 (ElementGroup[Fixture]([Fixture.get_by_id(1), Fixture.get_by_id(380)]),
                                  (ElementGroup[Fixture]([Fixture.get_by_id(1)]), ElementGroup[Fixture]([Fixture.get_by_id(380)]))),
                             ]
                             )
    def test_split_fixtures_by_finished(self, fixture_group: ElementGroup[Fixture], expected_output: tuple[ElementGroup[Fixture], ElementGroup[Fixture]]) -> None:
        assert Fixture.split_fixtures_by_finished(fixture_group) == expected_output

    @pytest.mark.parametrize("fixture_group,event,expected_output",
                             [
                                 (ElementGroup[Fixture]([Fixture.get_by_id(1), Fixture.get_by_id(380)]), Event.get_by_id(1),
                                  (ElementGroup[Fixture]([Fixture.get_by_id(1)]))),
                             ]
                             )
    def test_get_fixtures_in_event(self, fixture_group: ElementGroup[Fixture], event: Event, expected_output: ElementGroup[Fixture]) -> None:
        assert Fixture.get_fixtures_in_event(fixture_group, event) == expected_output

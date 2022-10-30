import pytest
from typing import Any, TypeVar, Union
from fpld.elements.element import ElementGroup
from .examples import PLAYERS, TEAM_DF
from .test_elements import Element, ElementClass
from fpld.elements.fplelems import Player
from fpld.elements.player import BasePlayer
from fpld.elements.player import _player


class PlayerElement(Element[_player]):
    expected: dict[str, Any] = {
        "__str__": "",
        "__repr__": "",
        "unique_id": 0,
        "goal_contributions": 0,
        "ppm": 0.0,
        "transfer_diff": 0
    }

    def test_goal_contributions(self) -> None:
        assert self.element_to_test.goal_contributions == self.expected["goal_contributions"]

    def test_ppm(self) -> None:
        assert self.element_to_test.ppm == self.expected["ppm"]

    def test_transfer_diff(self) -> None:
        assert self.element_to_test.transfer_diff == self.expected["transfer_diff"]


class TestBasePlayerExample(PlayerElement[BasePlayer]):
    element_to_test: BasePlayer = BasePlayer.get_by_id(427)
    expected: dict[str, Any] = {
        "__str__": "Kane",
        "__repr__": "BasePlayer(element_type=4, team=18, web_name='Kane')",
        "unique_id": 427,
        "goal_contributions": element_to_test.goals_scored + element_to_test.assists,
        "ppm": round(element_to_test.total_points / element_to_test.now_cost, 3),
        "transfer_diff": element_to_test.transfers_in_event - element_to_test.transfers_out_event
    }


class TestPlayerExample(PlayerElement[Player]):
    element_to_test: Player = Player.get_by_id(427)
    expected: dict[str, Any] = {
        "__str__": "Kane",
        "__repr__": "Player(element_type=Position(singular_name='Forward'), team=Team(name='Spurs'), web_name='Kane')",
        "unique_id": 427,
        "goal_contributions": element_to_test.goals_scored + element_to_test.assists,
        "ppm": round(element_to_test.total_points / element_to_test.now_cost, 3),
        "transfer_diff": element_to_test.transfers_in_event - element_to_test.transfers_out_event
    }

    def test_in_full(self) -> None:
        self.element_to_test.in_full()


class TestPlayerClass(ElementClass[Player]):
    class_to_test = Player
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/"
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (427, Player.get(web_name="Kane")[0]),
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[Player, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    @pytest.mark.parametrize("player_pool,lower,upper,include_boundaries,expected_output",
                             [
                                 (Player.get_all(), 120, 150, True, ElementGroup[Player]([PLAYERS["MID2"], PLAYERS["MID1"], PLAYERS["FWD2"]])),
                                 (ElementGroup[Player]([]), 0, 200, True, ElementGroup[Player]([]))
                             ]
                             )
    def test_in_cost_range(self, player_pool: ElementGroup[Player], lower: int, upper: int, include_boundaries: bool, expected_output: ElementGroup[Player]) -> None:
        group = self.class_to_test.in_cost_range(player_pool, lower=lower, upper=upper, include_boundaries=include_boundaries)
        assert group.to_list() == expected_output.to_list()

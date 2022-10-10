from copy import deepcopy
from typing import Any
import pytest
import fpld
from fpld.team.validation import FPLTeamVD, FPLTeamConstraint, LPSquad


if __name__ == "__main__":
    from examples import PLAYERS, VALID_SQUAD
else:
    from .examples import PLAYERS, VALID_SQUAD


class TestFPLTeamExample:
    team_to_test: fpld.Squad = fpld.Squad(*VALID_SQUAD)
    with open("./tests/squad_str.txt", "r") as f:
        expected_str = f.read()

    expected: dict[str, Any] = {
        "formation": "4-4-2",
        "__str__": expected_str
    }

    def test_str(self) -> None:
        assert str(self.team_to_test) == self.expected["__str__"]

    def test_formation(self) -> None:
        assert str(self.team_to_test.formation) == self.expected["formation"]

    def test_change_captain_in_team(self) -> None:
        valid_team_copy = deepcopy(self.team_to_test)

        valid_team_copy.captain = PLAYERS["GK1"]

    def test_change_vice_captain_in_team(self) -> None:
        valid_team_copy = deepcopy(self.team_to_test)

        valid_team_copy.vice_captain = PLAYERS["GK1"]

    def test_change_captain_not_in_team(self) -> None:
        valid_team_copy = deepcopy(self.team_to_test)

        with pytest.raises(Exception):
            valid_team_copy.captain = PLAYERS["DEF6"]

    def test_change_vice_captain_not_in_team(self) -> None:
        valid_team_copy = deepcopy(self.team_to_test)

        with pytest.raises(Exception):
            valid_team_copy.vice_captain = PLAYERS["DEF6"]


@pytest.mark.xfail
def test_change_captain_to_vice_captain(valid_team: fpld.Squad) -> None:
    valid_team_copy = deepcopy(valid_team)

    with pytest.raises(Exception):
        valid_team_copy.vice_captain = valid_team_copy.captain


class TestFPLTeamCases:
    def test_random_insufficient_pool(self) -> None:
        with pytest.raises(Exception):  # More specific
            fpld.Squad.random([PLAYERS["FWD1"]])

    def test_random_sufficient_pool(self) -> None:
        players = fpld.Player.get_all()

        fpld.Squad.random(players)

    @pytest.mark.xfail
    def test_optimal_squad(self) -> None:
        player_pool = {
            PLAYERS["GK1"]: [1.0], PLAYERS["GK2"]: [1.0],
            PLAYERS["DEF1"]: [1.0], PLAYERS["DEF2"]: [1.0], PLAYERS["DEF3"]: [1.0], PLAYERS["DEF4"]: [1.0], PLAYERS["DEF5"]: [1.0],
            PLAYERS["MID1"]: [1.0], PLAYERS["MID2"]: [1.0], PLAYERS["MID3"]: [1.0], PLAYERS["MID4"]: [1.0], PLAYERS["MID5"]: [1.0], PLAYERS["MID6"]: [0.0],
            PLAYERS["FWD1"]: [1.0], PLAYERS["FWD2"]: [1.0], PLAYERS["FWD3"]: [1.0]
        }

        squad = fpld.Squad.optimal_team(player_pool, budget=2000, budget_interval=600)

        assert PLAYERS["MID6"] not in squad.starting_team or PLAYERS["MID6"] not in squad.bench


@pytest.fixture
def vd() -> FPLTeamVD:
    return FPLTeamVD()


# validation.py


'''def test_fplteamvd_num_players_in_starting_valid(valid_team_group: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player], vd: FPLTeamVD) -> None:
    starting_team = valid_team_group[0]

    vd.num_players_in_starting(starting_team)


def test_fplteamvd_num_players_in_starting_invalid(invalid_position_not_enough_group: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player], vd: FPLTeamVD) -> None:
    starting_team = invalid_position_not_enough_group[0]
    starting_team.pop()

    with pytest.raises(Exception):  # More specific
        vd.num_players_in_starting(starting_team)


def test_fplteamvd_num_players_in_team_invalid(valid_team_group: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player], vd: FPLTeamVD) -> None:
    full_team = valid_team_group[0] + valid_team_group[1] + PLAYERS["MID6"]

    with pytest.raises(Exception):  # More specific
        vd.num_players_in_team(full_team)


def test_fplteamvd_num_players_from_teams_invalid(invalid_extra_team_players_group: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player], vd: FPLTeamVD) -> None:
    full_team = invalid_extra_team_players_group[0] + invalid_extra_team_players_group[1]

    with pytest.raises(Exception):  # More specific
        vd.num_players_from_teams(full_team)'''


class TestLPSquad:
    def test_player_pool(self) -> None:
        pass

    def test_budget(self) -> None:
        pass

    def test_budget_bounds(self) -> None:
        pass

    def test_required_players(self) -> None:
        pass

    def test_values_for_player(self) -> None:
        pass

    def test_player_lp_variable_in_pool(self) -> None:
        pass

    def test_player_lp_variable_not_in_pool(self) -> None:
        pass

    def test_new_team(self) -> None:
        pass

    def test_new_squad(self) -> None:
        pass


class TestFPLTeamConstraints:
    pass


if __name__ == "__main__":
    pytest.main([__file__])

from copy import deepcopy
from typing import Any
import pytest
import fpld
from fpld.team.validation import FPLTeamVD, FPLTeamConstraint, LPSquad
import random
from .examples import PLAYERS, VALID_SQUAD, INVALID_SQUAD_EXTRA_TEAM_PLAYERS, INVALID_SQUAD_NOT_ENOUGH_GROUP


class TestFPLTeamExample:
    team_to_test: fpld.Squad = fpld.Squad(*VALID_SQUAD)
    with open("./tests/squad_str.txt", "r") as f:
        expected_str = f.read()

    expected: dict[str, Any] = {
        "formation": "4-4-2",
        "__str__": expected_str,
        "captain": PLAYERS["FWD1"],
        "vice_captain": PLAYERS["FWD2"]
    }

    def test_str(self) -> None:
        assert str(self.team_to_test) == self.expected["__str__"]

    def test_formation(self) -> None:
        assert str(self.team_to_test.formation) == self.expected["formation"]

    def test_captain(self) -> None:
        assert self.team_to_test.captain == self.expected["captain"]

    def test_vice_captain(self) -> None:
        assert self.team_to_test.vice_captain == self.expected["vice_captain"]

    def test_cost(self) -> None:
        assert isinstance(self.team_to_test.cost, int)

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
    def test_change_captain_to_vice_captain(self) -> None:
        valid_team_copy = deepcopy(self.team_to_test)

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


# validation.py


class TestFPLTeamVDCases:
    vd = FPLTeamVD()
    valid_group = VALID_SQUAD
    extra_team_players_group = INVALID_SQUAD_EXTRA_TEAM_PLAYERS
    not_enough_defenders_starting_group = INVALID_SQUAD_NOT_ENOUGH_GROUP

    def test_check_unordered(self) -> None:
        starting_team = self.valid_group[0]
        bench = self.valid_group[1]
        random.shuffle(starting_team)
        random.shuffle(bench)

        self.vd.check(starting_team, bench)

    def test_check_ordered(self) -> None:
        starting_team = self.valid_group[0]
        bench = self.valid_group[1]

        self.vd.check(starting_team, bench)

    def test_num_players_in_starting_invalid(self) -> None:
        starting_team = deepcopy(self.valid_group[0])
        starting_team.pop()
        # Becomes 10 players as 4-4-1

        with pytest.raises(Exception):  # More specific
            self.vd.num_players_in_starting(starting_team)

    def test_num_players_in_team_invalid(self) -> None:
        full_team = self.valid_group[0] + self.valid_group[1]
        full_team.append(PLAYERS["MID6"])

        with pytest.raises(Exception):  # More specific
            self. vd.num_players_in_team(full_team)

    def test_num_players_from_teams_invalid(self) -> None:
        full_team = self.extra_team_players_group[0] + self.extra_team_players_group[1]

        with pytest.raises(Exception):  # More specific
            self.vd.num_players_from_teams(full_team)

    def test_num_players_in_position_inbalanced_full_team(self) -> None:
        starting_team = deepcopy(self.valid_group[0])
        starting_team.remove(PLAYERS["FWD2"])
        starting_team.remove(PLAYERS["FWD1"])
        starting_team.append(PLAYERS["MID5"])
        starting_team.append(PLAYERS["DEF5"])
        bench = deepcopy(self.valid_group[1])
        bench.append(PLAYERS["FWD1"])
        bench.append(PLAYERS["FWD2"])
        # becomes 1-5-5-0

        with pytest.raises(Exception):  # More specific
            self.vd.num_players_in_position(starting_team, bench)

    def test_num_players_in_position_inbalanced_starting_team(self) -> None:
        starting_team = self.not_enough_defenders_starting_group[0]
        bench = self.not_enough_defenders_starting_group[1]

        with pytest.raises(Exception):  # More specific
            self.vd.num_players_in_position(starting_team, bench)


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

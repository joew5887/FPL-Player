from copy import deepcopy
from typing import Any
import pytest
import fpld
from fpld.team.validation import FPLTeamVD, LPSquad
import random
from .examples import PLAYERS, VALID_SQUAD, INVALID_SQUAD_EXTRA_TEAM_PLAYERS, INVALID_SQUAD_NOT_ENOUGH_GROUP, LONG_BENCH_VALID_SQUAD


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


class TestFPLTeamLongBenchStr(TestFPLTeamExample):
    team_to_test: fpld.Squad = fpld.Squad(*LONG_BENCH_VALID_SQUAD)
    with open("./tests/long_bench_squad_str.txt", "r") as f:
        expected_str = f.read()

    expected: dict[str, Any] = {
        "formation": "4-3-3",
        "__str__": expected_str,
        "captain": PLAYERS["FWD1"],
        "vice_captain": PLAYERS["FWD2"]
    }


class TestFPLTeamCases:
    def test_random_insufficient_pool(self) -> None:
        with pytest.raises(Exception):  # More specific
            fpld.Squad.random([PLAYERS["FWD1"]])

    def test_random_sufficient_pool(self) -> None:
        players = fpld.Player.get_all()

        fpld.Squad.random(players, 1000, 997, [])

    def test_optimal_squad(self) -> None:
        player_pool = {
            PLAYERS["GK1"]: [1.0], PLAYERS["GK2"]: [1.0],
            PLAYERS["DEF1"]: [1.0], PLAYERS["DEF2"]: [1.0], PLAYERS["DEF3"]: [1.0], PLAYERS["DEF4"]: [1.0], PLAYERS["DEF5"]: [1.0],
            PLAYERS["MID1"]: [1.0], PLAYERS["MID2"]: [1.0], PLAYERS["MID3"]: [1.0], PLAYERS["MID4"]: [1.0], PLAYERS["MID5"]: [1.0], PLAYERS["MID6"]: [0.0],
            PLAYERS["FWD1"]: [1.0], PLAYERS["FWD2"]: [1.0], PLAYERS["FWD3"]: [1.0]
        }

        squad = fpld.Squad.optimal_team(player_pool, 3000, 500, [])

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
    pass


class TestFPLTeamConstraints:
    PLAYER_POOL: dict[fpld.Player, list[int]] = {p: [p.yellow_cards] for p in fpld.Player.get_all()}

    @pytest.mark.parametrize("num_players", [15, 0])
    def test_set_num_players_constraint(self, num_players: int) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(num_players)
        sol = lp_squad.solve()

        assert len(sol) == num_players

    def test_set_num_players_higher_than_player_pool(self) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)
        max_players = len(self.PLAYER_POOL) + 1

        with pytest.raises(ValueError):
            lp_squad.constraint_engine.set_num_players(max_players)

    def test_reset_problem(self) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(11)
        lp_squad.constraint_engine.reset_problem()

        lp_squad.constraint_engine.set_num_players(10)
        sol = lp_squad.solve()

        assert len(sol) == 10

    @pytest.mark.parametrize("num_players_same_club", [3, 1])
    def test_num_players_same_club_constraint(self, num_players_same_club: int) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(10)
        lp_squad.constraint_engine.num_players_same_club(num_players_same_club)
        sol = lp_squad.solve()
        group = fpld.ElementGroup[fpld.Player](sol)

        assert any([len(players_from_team) <= num_players_same_club for players_from_team in group.group_by("team").values()])

    def test_zero_players_same_club_constraint(self) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.num_players_same_club(0)
        sol = lp_squad.solve()

        assert sol == []

    @pytest.mark.parametrize("budget_ub,budget_lb", [(1000, 990), (1000, 1000)])
    def test_budget_constraint(self, budget_ub: int, budget_lb: int) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(10)
        lp_squad.constraint_engine.budget(budget_ub, budget_lb)
        sol = lp_squad.solve()

        squad_cost = sum([p.now_cost for p in sol])

        assert budget_lb <= squad_cost and squad_cost <= budget_ub

    def test_budget_lb_bigger_constraint(self) -> None:
        budget_ub = 990
        budget_lb = 1000

        lp_squad = LPSquad(self.PLAYER_POOL)

        with pytest.raises(ValueError):
            lp_squad.constraint_engine.budget(budget_ub, budget_lb)

    def test_zero_budget_constraint(self) -> None:
        budget_ub = 0
        budget_lb = 0

        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.budget(budget_ub, budget_lb)
        sol = lp_squad.solve()

        assert sol == []

    def test_required_players(self) -> None:
        required_players = [PLAYERS["MID1"]]

        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(10)
        lp_squad.constraint_engine.required_players(required_players)
        sol = lp_squad.solve()

        assert PLAYERS["MID1"] in sol

    def test_required_player_not_in_pool(self) -> None:
        required_players = [PLAYERS["MID1"]]
        player_pool = {k: v for k, v in self.PLAYER_POOL.items() if k != PLAYERS["MID1"]}
        assert not (PLAYERS["MID1"] in player_pool)

        lp_squad = LPSquad(player_pool)

        with pytest.raises(Exception):
            lp_squad.constraint_engine.required_players(required_players)

    def test_too_many_required_players(self) -> None:
        required_players = [PLAYERS["MID1"], PLAYERS["MID2"]]
        player_pool = {PLAYERS["MID1"]: [PLAYERS["MID1"].goals_scored]}

        lp_squad = LPSquad(player_pool)

        lp_squad.constraint_engine.set_num_players(1)

        with pytest.raises(Exception):
            lp_squad.constraint_engine.required_players(required_players)

    @pytest.mark.parametrize("position,min_players,max_players", [(fpld.Position.get_by_name("DEF"), 5, 5), (fpld.Position.get_by_name("DEF"), 3, 5)])
    def test_position_min_max(self, position: fpld.Position, min_players: int, max_players: int) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(max_players)
        lp_squad.constraint_engine.position_min_max(position, min_players, max_players)
        sol = lp_squad.solve()

        assert min_players <= len(sol) and len(sol) <= max_players

    def test_position_min_max_min_bigger(self) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)
        position = fpld.Position.get_by_name("MID")
        max_players = 5
        min_players = 6

        with pytest.raises(ValueError):
            lp_squad.constraint_engine.position_min_max(position, min_players, max_players)

    def test_invalid_problem(self) -> None:
        lp_squad = LPSquad(self.PLAYER_POOL)

        lp_squad.constraint_engine.set_num_players(11)
        lp_squad.constraint_engine.position_min_max(fpld.Position.get_by_name("MID"), 12, 12)

        with pytest.raises(Exception):
            lp_squad.solve()

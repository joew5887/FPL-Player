from copy import deepcopy
import pytest
import fpld
from fpld.team.validation import FPLTeamVD, FPLTeamConstraint, LPSquad


@pytest.fixture
def vd() -> FPLTeamVD:
    return FPLTeamVD()


@pytest.fixture
def valid_team_group() -> tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player]:
    starting_team = [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF4"],
        PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"],
        PLAYERS["FWD1"], PLAYERS["FWD2"]
    ]
    bench = [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["MID5"], PLAYERS["FWD3"]
    ]
    captain = PLAYERS["FWD1"]
    vice_captain = PLAYERS["FWD2"]

    return starting_team, bench, captain, vice_captain


@pytest.fixture
def valid_team(valid_team_group: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player]) -> fpld.Squad:
    return fpld.Squad(*valid_team_group)


@pytest.fixture
def invalid_extra_team_players_group() -> tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player]:
    starting_team = [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF6"],
        PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"],
        PLAYERS["FWD1"], PLAYERS["FWD2"]
    ]
    bench = [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["MID5"], PLAYERS["FWD3"]
    ]
    captain = PLAYERS["FWD1"]
    vice_captain = PLAYERS["FWD2"]

    return starting_team, bench, captain, vice_captain


@pytest.fixture
def invalid_position_not_enough_group() -> tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player]:
    starting_team = [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"],
        PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"], PLAYERS["MID5"],
        PLAYERS["FWD1"], PLAYERS["FWD2"], PLAYERS["FWD3"]
    ]
    bench = [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["DEF3"], PLAYERS["DEF4"]
    ]
    captain = PLAYERS["FWD1"]
    vice_captain = PLAYERS["FWD2"]

    return starting_team, bench, captain, vice_captain


@pytest.mark.xfail
def test_str(valid_team: fpld.Squad) -> None:
    team_str = str(valid_team)

    assert any([p.web_name in team_str for p in valid_team.starting_team + valid_team.bench])
    assert str(PLAYERS["FWD1"]) + " (C)" in team_str
    assert str(PLAYERS["FWD2"]) + " (VC)" in team_str


def test_formation(valid_team: fpld.Squad) -> None:
    formation_str = str(valid_team.formation)

    assert formation_str == "4-4-2"


def test_random_sufficient_pool() -> None:
    players = fpld.Player.get_all()

    fpld.Squad.random(players)


def test_random_insufficient_pool() -> None:
    with pytest.raises(Exception):  # More specific
        fpld.Squad.random([PLAYERS["FWD1"]])


@pytest.mark.xfail
def test_optimal_squad() -> None:
    player_pool = {
        PLAYERS["GK1"]: [1.0], PLAYERS["GK2"]: [1.0],
        PLAYERS["DEF1"]: [1.0], PLAYERS["DEF2"]: [1.0], PLAYERS["DEF3"]: [1.0], PLAYERS["DEF4"]: [1.0], PLAYERS["DEF5"]: [1.0],
        PLAYERS["MID1"]: [1.0], PLAYERS["MID2"]: [1.0], PLAYERS["MID3"]: [1.0], PLAYERS["MID4"]: [1.0], PLAYERS["MID5"]: [1.0], PLAYERS["MID6"]: [0.0],
        PLAYERS["FWD1"]: [1.0], PLAYERS["FWD2"]: [1.0], PLAYERS["FWD3"]: [1.0]
    }

    squad = fpld.Squad.optimal_team(player_pool, budget=2000, budget_interval=600)

    assert PLAYERS["MID6"] not in squad.starting_team or PLAYERS["MID6"] not in squad.bench


def test_change_captain_in_team(valid_team: fpld.Squad) -> None:
    valid_team_copy = deepcopy(valid_team)

    valid_team_copy.captain = PLAYERS["GK1"]


def test_change_vice_captain_in_team(valid_team: fpld.Squad) -> None:
    valid_team_copy = deepcopy(valid_team)

    valid_team_copy.vice_captain = PLAYERS["GK1"]


def test_change_captain_not_in_team(valid_team: fpld.Squad) -> None:
    valid_team_copy = deepcopy(valid_team)

    with pytest.raises(Exception):
        valid_team_copy.captain = PLAYERS["DEF6"]


def test_change_vice_captain_not_in_team(valid_team: fpld.Squad) -> None:
    valid_team_copy = deepcopy(valid_team)

    with pytest.raises(Exception):
        valid_team_copy.vice_captain = PLAYERS["DEF6"]


@pytest.mark.xfail
def test_change_captain_to_vice_captain(valid_team: fpld.Squad) -> None:
    valid_team_copy = deepcopy(valid_team)

    with pytest.raises(Exception):
        valid_team_copy.vice_captain = valid_team_copy.captain


# validation.py


def test_fplteamvd_num_players_in_starting_valid(valid_team_group: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player], vd: FPLTeamVD) -> None:
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
        vd.num_players_from_teams(full_team)


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
    from examples import PLAYERS
else:
    from .examples import PLAYERS

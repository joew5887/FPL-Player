import pytest
import fpld
from .examples import PLAYERS


@pytest.fixture
def valid_442_group() -> fpld.ElementGroup[fpld.Player]:
    return fpld.ElementGroup(
        [
            PLAYERS["GK1"], PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"],
            PLAYERS["DEF4"], PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"],
            PLAYERS["MID4"], PLAYERS["FWD1"], PLAYERS["FWD2"]
        ]
    )


@pytest.fixture
def invalid_no_gk_group() -> fpld.ElementGroup[fpld.Player]:
    return fpld.ElementGroup(
        [
            PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF4"],
            PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"],
            PLAYERS["MID5"], PLAYERS["FWD1"], PLAYERS["FWD2"]
        ]
    )


@ pytest.fixture
def invalid_not_11_group() -> fpld.ElementGroup[fpld.Player]:
    return fpld.ElementGroup(
        [
            PLAYERS["GK1"], PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"],
            PLAYERS["DEF4"], PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"],
            PLAYERS["FWD1"], PLAYERS["FWD2"]
        ]
    )


def test_valid_team(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    fpld.Formation.is_valid_team(valid_442_group)


def test_str(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    assert str(fpld.Formation(valid_442_group)) == "4-4-2"


def test_as_numbers_ignore_gk(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    expected = {fpld.Position.get_by_name(
        "DEF"): 4, fpld.Position.get_by_name("MID"): 4, fpld.Position.get_by_name("FWD"): 2}

    assert fpld.Formation(valid_442_group).as_numbers() == expected


def test_as_numbers_include_gk(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    expected = {fpld.Position.get_by_name("GKP"): 1, fpld.Position.get_by_name(
        "DEF"): 4, fpld.Position.get_by_name("MID"): 4, fpld.Position.get_by_name("FWD"): 2}

    assert fpld.Formation(valid_442_group).as_numbers(False) == expected


def test_as_players_include_gk(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    expected = {
        fpld.Position.get_by_name("GKP"): [PLAYERS["GK1"]],
        fpld.Position.get_by_name("DEF"): [PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF4"]],
        fpld.Position.get_by_name("MID"): [PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"]],
        fpld.Position.get_by_name("FWD"): [PLAYERS["FWD1"], PLAYERS["FWD2"]]
    }

    assert fpld.Formation(valid_442_group).as_players() == expected


def test_as_players_ignore_gk(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    expected = {
        fpld.Position.get_by_name("DEF"): [PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF4"]],
        fpld.Position.get_by_name("MID"): [PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"]],
        fpld.Position.get_by_name("FWD"): [PLAYERS["FWD1"], PLAYERS["FWD2"]]
    }

    assert fpld.Formation(valid_442_group).as_players(True) == expected


def test_as_text(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    formation = fpld.Formation(valid_442_group)

    assert any([p.web_name in formation.as_text() for p in valid_442_group])


def test_no_gk_error(invalid_no_gk_group: fpld.ElementGroup[fpld.Player]) -> None:
    with pytest.raises(fpld.elements.element.IDMatchesZeroElements):
        fpld.Formation.is_valid_team(invalid_no_gk_group)


def test_not_11_players_error(invalid_not_11_group: fpld.ElementGroup[fpld.Player]) -> None:
    with pytest.raises(Exception):
        fpld.Formation.is_valid_team(invalid_not_11_group)

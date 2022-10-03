import pytest
import fpld


GK = fpld.Player.get_by_id(425)  # Lloris
DEF1 = fpld.Player.get_by_id(443)  # Romero
DEF2 = fpld.Player.get_by_id(106)  # Dunk
DEF3 = fpld.Player.get_by_id(357)  # Trippier
DEF4 = fpld.Player.get_by_id(332)  # Shaw
MID1 = fpld.Player.get_by_id(301)  # KDB
MID2 = fpld.Player.get_by_id(440)  # Bentancur
MID3 = fpld.Player.get_by_id(325)  # Kalvin Phillips
MID4 = fpld.Player.get_by_id(407)  # JWP
FWD1 = fpld.Player.get_by_id(427)  # Kane
FWD2 = fpld.Player.get_by_id(318)  # Haaland
MID5 = fpld.Player.get_by_id(233)  # Jack Harrison


@pytest.fixture
def valid_442_group() -> fpld.ElementGroup[fpld.Player]:
    return fpld.ElementGroup([GK, DEF1, DEF2, DEF3, DEF4, MID1, MID2, MID3, MID4, FWD1, FWD2])


@pytest.fixture
def invalid_no_gk_group() -> fpld.ElementGroup[fpld.Player]:
    return fpld.ElementGroup([DEF1, DEF2, DEF3, DEF4, MID1, MID2, MID3, MID4, MID5, FWD1, FWD2])


@pytest.fixture
def invalid_not_11_group() -> fpld.ElementGroup[fpld.Player]:
    return fpld.ElementGroup([GK, DEF1, DEF2, DEF3, DEF4, MID1, MID2, MID3, FWD1, FWD2])


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
    expected = {fpld.Position.get_by_name("GKP"): [GK], fpld.Position.get_by_name(
        "DEF"): [DEF1, DEF2, DEF3, DEF4], fpld.Position.get_by_name("MID"): [MID1, MID2, MID3, MID4], fpld.Position.get_by_name("FWD"): [FWD1, FWD2]}

    assert fpld.Formation(valid_442_group).as_players() == expected


def test_as_players_ignore_gk(valid_442_group: fpld.ElementGroup[fpld.Player]) -> None:
    expected = {fpld.Position.get_by_name(
        "DEF"): [DEF1, DEF2, DEF3, DEF4], fpld.Position.get_by_name("MID"): [MID1, MID2, MID3, MID4], fpld.Position.get_by_name("FWD"): [FWD1, FWD2]}

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


if __name__ == "__main__":
    pytest.main([__file__])

import fpld
import pandas as pd


PLAYERS = {
    "GK1": fpld.Player.get_by_id(425),  # Lloris
    "GK2": fpld.Player.get_by_id(81),  # Raya
    "DEF1": fpld.Player.get_by_id(443),  # Romero
    "DEF2": fpld.Player.get_by_id(106),  # Dunk
    "DEF3": fpld.Player.get_by_id(357),  # Trippier
    "DEF4": fpld.Player.get_by_id(332),  # Shaw
    "DEF5": fpld.Player.get_by_id(272),  # Fofana
    "DEF6": fpld.Player.get_by_id(302),  # Stones
    "MID1": fpld.Player.get_by_id(301),  # KDB
    "MID2": fpld.Player.get_by_id(283),  # Salah
    "MID3": fpld.Player.get_by_id(325),  # Kalvin Phillips
    "MID4": fpld.Player.get_by_id(407),  # JWP
    "MID5": fpld.Player.get_by_id(233),  # Jack Harrison
    "MID6": fpld.Player.get_by_id(261),  # Maddison
    "FWD1": fpld.Player.get_by_id(427),  # Kane
    "FWD2": fpld.Player.get_by_id(318),  # Haaland
    "FWD3": fpld.Player.get_by_id(80),  # Toney
    "FWD4": fpld.Player.get_by_id(66)  # Solanke
}

POSITIONS = {
    "GKP": fpld.Position.get_by_id(1), "DEF": fpld.Position.get_by_id(2),
    "MID": fpld.Position.get_by_id(3), "MID": fpld.Position.get_by_id(4)
}

VALID_SQUAD: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player] = (
    [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF4"],
        PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"],
        PLAYERS["FWD1"], PLAYERS["FWD2"]
    ],
    [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["MID5"], PLAYERS["FWD3"]
    ],
    PLAYERS["FWD1"],
    PLAYERS["FWD2"]
)

LONG_BENCH_VALID_SQUAD: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player] = (
    [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF4"],
        PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID5"],
        PLAYERS["FWD1"], PLAYERS["FWD2"], PLAYERS["FWD3"]
    ],
    [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["MID4"], PLAYERS["MID1"]
    ],
    PLAYERS["FWD1"],
    PLAYERS["FWD2"]
)

INVALID_SQUAD_EXTRA_TEAM_PLAYERS: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player] = (
    [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"], PLAYERS["DEF3"], PLAYERS["DEF6"],
        PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"],
        PLAYERS["FWD1"], PLAYERS["FWD2"]
    ],
    [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["MID5"], PLAYERS["FWD3"]
    ],
    PLAYERS["FWD1"],
    PLAYERS["FWD2"]
)

INVALID_SQUAD_NOT_ENOUGH_GROUP: tuple[list[fpld.Player], list[fpld.Player], fpld.Player, fpld.Player] = (
    [
        PLAYERS["GK1"],
        PLAYERS["DEF1"], PLAYERS["DEF2"],
        PLAYERS["MID1"], PLAYERS["MID2"], PLAYERS["MID3"], PLAYERS["MID4"], PLAYERS["MID5"],
        PLAYERS["FWD1"], PLAYERS["FWD2"], PLAYERS["FWD3"]
    ],
    [
        PLAYERS["GK2"], PLAYERS["DEF5"], PLAYERS["DEF3"], PLAYERS["DEF4"]
    ],
    PLAYERS["FWD1"],
    PLAYERS["FWD2"]
)

TEAM_DF = pd.DataFrame(
    {
        "name":
            [
                "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
                "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leicester",
                "Leeds", "Liverpool", "Man City", "Man Utd", "Newcastle",
                "Nott'm Forest", "Southampton", "Spurs", "West Ham", "Wolves"
            ],
        "short_name":
            [
                "ARS", "AVL", "BOU", "BRE", "BHA", "CHE", "CRY", "EVE", "FUL", "LEI",
                "LEE", "LIV", "MCI", "MUN", "NEW", "NFO", "SOU", "TOT", "WHU", "WOL"
            ]
    },
    columns=["name", "short_name"],
    index=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
)

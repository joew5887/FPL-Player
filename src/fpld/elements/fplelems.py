from typing import TypeVar
from .team import BaseTeam
from .player import BasePlayer
from .fixture import BaseFixture
from .event import BaseEvent
from functools import cache


team = TypeVar("team", bound="Team")
player = TypeVar("player", bound="Player")
event = TypeVar("event", bound="Event")
fixture = TypeVar("fixture", bound="Fixture")


class Team(BaseTeam[team]):
    pass


class Player(BasePlayer[player]):
    team: Team

    def __init__(self, **attr_to_value):
        attr_to_value["team"] = id_to_team(attr_to_value["team"])
        super().__init__(**attr_to_value)


class Event(BaseEvent[event]):
    most_selected: Player
    most_transferred_in: Player
    top_element: Player
    most_captained: Player
    most_vice_captained: Player

    def __init__(self, **attr_to_value):
        attr_to_value["most_selected"] = \
            id_to_player(attr_to_value["most_selected"])
        attr_to_value["most_transferred_in"] = \
            id_to_player(attr_to_value["most_transferred_in"])
        attr_to_value["top_element"] = \
            id_to_player(attr_to_value["top_element"])
        attr_to_value["most_captained"] = \
            id_to_player(attr_to_value["most_captained"])
        attr_to_value["most_vice_captained"] = \
            id_to_player(attr_to_value["most_vice_captained"])
        super().__init__(**attr_to_value)


class Fixture(BaseFixture[fixture]):
    event: Event
    team_h: Team
    team_a: Team

    def __init__(self, **attr_to_value):
        attr_to_value["event"] = Event.get_from_api(
            **{Event.unique_id_col: attr_to_value["event"]})[0]
        attr_to_value["team_h"] = id_to_team(attr_to_value["team_h"])
        attr_to_value["team_a"] = id_to_team(attr_to_value["team_a"])
        super().__init__(**attr_to_value)


@cache
def id_to_team(team_id: int) -> Team:
    team = Team.get_from_api(**{"id": team_id})

    if not (id_uniqueness(team)):
        raise Exception(f"Number of players found is {len(team)}, not 1.")

    return team[0]


@cache
def id_to_player(player_id: int) -> Player:
    player = Player.get_from_api(**{"id": player_id})

    if not (id_uniqueness(player)):
        raise Exception(f"Number of players found is {len(player)}, not 1.")

    return player[0]


def id_uniqueness(results: list) -> bool:
    return len(results) == 1

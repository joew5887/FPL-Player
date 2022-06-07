from .fplelems import (Team, Player, Fixture, Event)
from .team import BaseTeam
from .player import BasePlayer
from .fixture import BaseFixture
from .event import BaseEvent
from .position import Position
from .labels import Label


def player_search(teams: list[Team], positions: list[Position], *, sort_by: str = "web_name", reverse: bool = True) -> list[Player]:
    players = []

    for team in teams:
        for player in team.players:
            if player.element_type in positions:
                players.append(player)

    players_sorted = Player.sort(players, sort_by, reverse=reverse)

    return players_sorted

from __future__ import annotations
from typing import TypeVar, Any, Union
from .team import BaseTeam
from .player import BasePlayer
from .fixture import BaseFixture
from .event import BaseEvent
from functools import cache
from dataclasses import dataclass, field


team = TypeVar("team", bound="Team")
player = TypeVar("player", bound="Player")
event = TypeVar("event", bound="Event")
fixture = TypeVar("fixture", bound="Fixture")


@dataclass(frozen=True, order=True, kw_only=True)
class Team(BaseTeam[team]):
    #players: list[Player] = field(hash=False, repr=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        #new_instance["players"] = Player.get(team=new_instance["id"])

        return new_instance

    @property
    def players(self) -> list[Player]:
        return Player.get(team=self.id)

    def player_total(self, *cols: tuple[str]) -> Union[float, int]:
        total = 0

        player: Player
        for player in self.players:
            for col in cols:
                try:
                    value = getattr(player, col)
                except AttributeError:
                    raise AttributeError(f"Attribute, '{col}', doesn't exist.")
                else:
                    if not isinstance(value, (float, int)):
                        raise AttributeError(
                            f"'{col}' must return float or int value.")

                total += value

        return total

    def total_goal_contributions(self, *, include_goals: bool = True, include_assists: bool = True) -> int:
        cols = []
        if include_goals:
            cols.append("goals_scored")

        if include_assists:
            cols.append("assists")

        return self.player_total(*cols)


@dataclass(frozen=True, order=True, kw_only=True)
class Player(BasePlayer[player]):
    team: Team = field(hash=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["team"] = Team.get_by_id(new_instance["team"])

        return new_instance


@dataclass(frozen=True, order=True, kw_only=True)
class Event(BaseEvent[event]):
    most_selected: Player = field(hash=False, repr=False)
    most_transferred_in: Player = field(hash=False, repr=False)
    top_element: Player = field(hash=False, repr=False)
    most_captained: Player = field(hash=False, repr=False)
    most_vice_captained: Player = field(hash=False, repr=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["most_selected"] = \
            Player.get_by_id(new_instance["most_selected"])
        new_instance["most_transferred_in"] = \
            Player.get_by_id(new_instance["most_transferred_in"])
        new_instance["top_element"] = \
            Player.get_by_id(new_instance["top_element"])
        new_instance["most_captained"] = \
            Player.get_by_id(new_instance["most_captained"])
        new_instance["most_vice_captained"] = \
            Player.get_by_id(new_instance["most_vice_captained"])

        return new_instance


@dataclass(frozen=True, order=True, kw_only=True)
class Fixture(BaseFixture[fixture]):
    event: Event = field(hash=False)
    team_h: Team = field(hash=False)
    team_a: Team = field(hash=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["event"] = Event.get_by_id(new_instance["event"])
        new_instance["team_h"] = Team.get_by_id(new_instance["team_h"])
        new_instance["team_a"] = Team.get_by_id(new_instance["team_a"])

        return new_instance

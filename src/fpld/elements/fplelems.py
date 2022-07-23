from __future__ import annotations
from typing import TypeVar, Any, Union
from fpld.constants import URLS
from fpld.util.percent import percent
from fpld.util import API
from .team import BaseTeam
from .player import BasePlayer, BasePlayerFull, BasePlayerHistory, BasePlayerFixtures, BasePlayerHistoryPast
from .fixture import BaseFixture
from .event import BaseEvent
from .position import Position
from dataclasses import Field, dataclass, field
from fpld.util.attribute import CategoricalVar
from .element import ElementGroup


team = TypeVar("team", bound="Team")
player = TypeVar("player", bound="Player")
event = TypeVar("event", bound="Event")
fixture = TypeVar("fixture", bound="Fixture")


@dataclass(frozen=True, order=True, kw_only=True)
class Team(BaseTeam[team]):
    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        return new_instance

    @property
    def players(self) -> ElementGroup[Player]:
        return Player.get(team=self.id)

    def players_by_pos(self, position: Position) -> ElementGroup[Player]:
        return self.players.filter(element_type=position)

    def player_total(self, *cols: tuple[str], by_position: Position = None) -> Union[float, int]:
        if by_position is not None:
            players = self.players_by_pos(by_position)
        else:
            players = self.players

        total = 0

        player: Player
        for player in players:
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

    def total_goal_contributions(self, *, by_position: Position = None) -> int:
        cols = ["goals_scored", "assists"]

        return self.player_total(*cols, by_position=by_position)

    def get_all_fixtures(self) -> ElementGroup[fixture]:
        return Fixture.get_all_team_fixtures(self)

    def get_fixtures_by_gameweek(self) -> dict[Event, ElementGroup[fixture]]:
        all_team_fixtures = self.get_all_fixtures()

        return all_team_fixtures.group_by("event")

    def fixtures_from_event(self, event: Event) -> ElementGroup[fixture]:
        all_team_fixtures = self.get_all_fixtures()

        return all_team_fixtures.filter(event=event)


@dataclass(frozen=True, order=True, kw_only=True)
class PlayerFull(BasePlayerFull):
    def __init__(self, fixtures: PlayerFixtures, history: PlayerHistory, history_past: BasePlayerHistoryPast):
        self.__fixtures = fixtures
        self.__history = history
        self.__history_past = history_past

    @property
    def fixtures(self) -> BasePlayerFixtures:
        return self.__fixtures

    @property
    def history(self) -> PlayerHistory:
        return self.__history

    @property
    def history_past(self) -> BasePlayerHistoryPast:
        return self.__history_past

    @classmethod
    def from_id(cls, player_id: int) -> BasePlayerFull:
        url = URLS["ELEMENT-SUMMARY"].format(player_id)
        api = API(url)  # Need to have offline feature
        fixtures = PlayerFixtures.from_api(api.data["fixtures"])
        history = PlayerHistory.from_api(api.data["history"])
        history_past = BasePlayerHistoryPast.from_api(api.data["history_past"])
        return BasePlayerFull(fixtures, history, history_past)


@dataclass(frozen=True, kw_only=True)
class PlayerHistory(BasePlayerHistory):
    fixture: CategoricalVar[Fixture] = field(hash=False, repr=False)
    opponent_team: CategoricalVar[Team] = field(hash=False, repr=False)

    @classmethod
    def _edit_stat_from_api(cls, field: Field, attr_list: list[Any]) -> dict[str, list[Any]]:
        if field.name == "fixture":
            attr_list = [Fixture.get_by_id(id_) for id_ in attr_list]
        elif field.name == "opponent_team":
            attr_list = [Team.get_by_id(id_) for id_ in attr_list]

        return attr_list


@dataclass(frozen=True, kw_only=True)
class PlayerFixtures(BasePlayerFixtures):
    fixture: CategoricalVar[Fixture] = field(hash=False, repr=False)

    @classmethod
    def _edit_stat_from_api(cls, field: Field, attr_list: list[Any]) -> dict[str, list[Any]]:
        if field.name == "fixture":
            attr_list = [Fixture.get_by_id(id_) for id_ in attr_list]

        return attr_list


@dataclass(frozen=True, order=True, kw_only=True)
class Player(BasePlayer[player]):
    team: Team = field(hash=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["team"] = Team.get_by_id(new_instance["team"])

        return new_instance

    @property
    def percent_pos(self) -> float:
        position_total = self.team.total_goal_contributions(
            by_position=self.element_type)
        return percent(self.goal_contributions, position_total)

    @property
    def percent_team(self) -> float:
        team_total = self.team.total_goal_contributions()
        return percent(self.goal_contributions, team_total)

    def in_full(self) -> PlayerFull:
        return PlayerFull.from_id(self.id)


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

    @property
    def fixtures(self) -> ElementGroup[Fixture]:
        return Fixture.get(event=self)


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

    @classmethod
    def get_team_fixtures(cls, team: Team) -> ElementGroup[fixture]:
        return super().get_all_team_fixtures(team.id)

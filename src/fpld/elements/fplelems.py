from __future__ import annotations
import math
from typing import Any, Optional, Union
from ..constants import datetime_to_string
from ..util.percent import to_percent
from .team import BaseTeam
from .player import _Player
from .playerfull import _PlayerFull, _PlayerHistory, _PlayerHistoryPast
from .fixture import _Fixture
from .event import _Event
from .position import Position
from .labels import Label
from dataclasses import Field, dataclass, field
from ..util.attribute import CategoricalVar
from .element import ElementGroup
import pandas as pd


@dataclass(frozen=True, order=True, kw_only=True)
class Team(BaseTeam["Team"]):
    @property
    def fixture_score(self) -> float:
        """Gives a score for how hard upcoming fixtures are.

        Returns
        -------
        float
            The higher the score, the harder the fixtures.
        """
        all_fixtures = self.get_all_fixtures()
        fixtures_to_play = Fixture.split_fixtures_by_finished(all_fixtures)[1]
        all_fixtures_by_event = Fixture.group_fixtures_by_gameweek(
            fixtures_to_play)

        score: float = 0.0
        multiplier: float = 0.9

        i = 0
        for fixtures in all_fixtures_by_event.values():
            fixture: Fixture
            for fixture in fixtures:
                diff = fixture.get_difficulty(self)

                score += diff * multiplier
                multiplier = math.e ** (-0.4 * i)
                i += 1

        return score

    @property
    def players(self) -> ElementGroup[Player]:
        """Get all players for a team.

        Returns
        -------
        ElementGroup[Player]
            Unsorted group of all players for a team.
        """
        return Player.get(team=self.unique_id)

    '''def average_form(self) -> float:
        """Gets average form of playing players in a team.

        Returns
        -------
        float
            Non-rounded average of team form.
        """
        eligible_players: list[Player] = []
        for player in self.players:
            player_full = player.in_full()

            if len(player_full.history.minutes.values) == 0:
                continue

            if player_full.history.minutes.values[-1] > 0:
                eligible_players.append(player)

        form_sum = sum(p.form for p in eligible_players)

        return form_sum / len(eligible_players)'''

    def get_all_fixtures(self) -> ElementGroup[Fixture]:
        """Gets all fixtures and results for a team.

        Returns
        -------
        ElementGroup[fixture]
            Team fixtures and results sorted by kickoff time.
        """
        return Fixture.get_all_team_fixtures(self.unique_id)

    def players_by_pos(self, position: Position) -> ElementGroup[Player]:
        """Gets all players from a team in a certain position.

        Parameters
        ----------
        position : Position
            Position to filter by.

        Returns
        -------
        ElementGroup[Player]
            All players from the team that play in that position.
        """
        return self.players.filter(element_type=position)

    def player_total(self, *cols: str, by_position: Optional[Position] = None) -> float:
        """Total points for all the players in a team, for a given attribute.

        Parameters
        ----------
        by_position : Optional[Position], optional
            Position to filter, None means all positions, by default None

        Returns
        -------
        float
            Total points.

        Raises
        ------
        AttributeError
            Attribute must exist in 'Player' fields.
        AttributeError
            Attribute found must be of type 'int' or 'float'.
        """
        if by_position is not None:
            players = self.players_by_pos(by_position)
        else:
            players = self.players

        total = 0.0

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

                total += float(value)

        return total

    def total_goal_contributions(self, *, by_position: Optional[Position] = None) -> int:
        """Total goal contributions for a team.

        Parameters
        ----------
        by_position : Optional[Position], optional
            Position to filter, None means all positions, by default None

        Returns
        -------
        int
            Total goals + total assists.
        """
        cols = ["goals_scored", "assists"]

        return int(self.player_total(*cols, by_position=by_position))


@dataclass(frozen=True, kw_only=True)
class PlayerHistory(_PlayerHistory["PlayerHistory"]):
    fixture: CategoricalVar[Fixture] = field(hash=False, repr=False)
    opponent_team: CategoricalVar[Team] = field(hash=False, repr=False)

    @classmethod
    def _edit_stat_from_api(cls, field: Field[Any], attr_list: list[Any]) -> list[Any]:
        if field.name == "fixture":
            attr_list = [Fixture.get_by_id(id_) for id_ in attr_list]
        elif field.name == "opponent_team":
            attr_list = [Team.get_by_id(id_) for id_ in attr_list]

        return attr_list

    @classmethod
    def from_api(cls, api_data: list[dict[str, Any]]) -> PlayerHistory:
        out: PlayerHistory = super().from_api(api_data)

        return out


@dataclass(frozen=True, kw_only=True)
class PlayerHistoryPast(_PlayerHistoryPast["PlayerHistoryPast"]):
    @classmethod
    def from_api(cls, api_data: list[dict[str, Any]]) -> PlayerHistoryPast:
        out: PlayerHistoryPast = super().from_api(api_data)

        return out


class PlayerFull(_PlayerFull[PlayerHistory, PlayerHistoryPast]):
    """Game by game, season by season data for a player, linked to other FPL elements.
    """

    @classmethod
    def from_player_id(cls, player_id: int) -> PlayerFull:
        data = cls.get_api(player_id)

        history = PlayerHistory.from_api(data["history"])
        history_past = PlayerHistoryPast.from_api(
            data["history_past"])

        return PlayerFull(history, history_past)


@dataclass(frozen=True, order=True, kw_only=True)
class Player(_Player["Player"]):
    """Player element, linked to other FPL elements.
    """
    team: Team = field(hash=False, compare=False)
    element_type: Position = field(hash=False, compare=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["element_type"] = Position.get_by_id(
            new_instance["element_type"])
        new_instance["team"] = Team.get_by_id(new_instance["team"])

        return new_instance

    @property
    def percent_pos(self) -> float:
        """Percent of player contribution to total team contributions
        in the player's position.

        Returns
        -------
        float
            player contributions / team position contributions.
        """
        position_total = self.team.total_goal_contributions(
            by_position=self.element_type)
        return to_percent(self.goal_contributions, position_total)

    @property
    def percent_team(self) -> float:
        """Percent of player  contributions to total team contributions.

        Returns
        -------
        float
            player contributions / team contributions.
        """
        team_total = self.team.total_goal_contributions()
        return to_percent(self.goal_contributions, team_total)

    '''def attribute_in_event(self, attribute: str, event: Event) -> list[Any]:
        """Gets all values of `attribute` for gameweek `event`.

        Parameters
        ----------
        attribute : str
            Attribute to find, e.g. 'total_points'.
        event : Event
            Event to find value for.

        Returns
        -------
        list[Any]
            All `attribute` values in gameweek `event`.

        Raises
        ------
        KeyError
            If `attribute` is not a key in each fixture.
        """
        in_full = self.in_full()
        fixtures_in_event = self.team.get_all_fixtures().filter(event=event.unique_id)
        values = []

        for fixture in in_full.history:
            if fixture["fixture"] not in fixtures_in_event:
                continue

            try:
                value = fixture[attribute]
            except KeyError:
                raise KeyError(f"{attribute} not in {fixture.keys()}")
            else:
                values.append(value)

        return values'''

    def in_full(self) -> PlayerFull:
        return PlayerFull.from_player_id(self.id)


@dataclass(frozen=True, order=True, kw_only=True)
class Event(_Event["Event"]):
    """Event / gameweek element, linked to other FPL elements.
    """
    most_selected: Player = field(hash=False, repr=False, compare=False)
    most_transferred_in: Player = field(hash=False, repr=False, compare=False)
    top_element: Player = field(hash=False, repr=False, compare=False)
    most_captained: Player = field(hash=False, repr=False, compare=False)
    most_vice_captained: Player = field(hash=False, repr=False, compare=False)

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
        """Get all fixtures / results from a gameweek.

        Returns
        -------
        ElementGroup[Fixture]
            Unordered list of fixtures in gameweek.
        """
        return Fixture.get(event=self)


@dataclass(frozen=True, order=True, kw_only=True)
class Fixture(_Fixture["Fixture"]):
    """Fixture / result element, linked to other FPL elements.
    """
    event: Event = field(hash=False, compare=False)
    team_h: Team = field(hash=False, compare=False)
    team_a: Team = field(hash=False, compare=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["event"] = Event.get_by_id(new_instance["event"])
        new_instance["team_h"] = Team.get_by_id(new_instance["team_h"])
        new_instance["team_a"] = Team.get_by_id(new_instance["team_a"])

        return new_instance

    def get_difficulty(self, team: Union[int, Team]) -> int:
        """Gets the difficulty of a fixture for a team.

        Parameters
        ----------
        team : Union[int, Team]
            Team to find difficulty for.

        Returns
        -------
        int
            Difficulty of the game for `team`.

        Raises
        ------
        ValueError
            If `team` is not in fixture.
        """
        if isinstance(team, Team):
            team_id = team.unique_id
        else:
            team_id = team

        if self.team_h.unique_id == team_id:
            return self.team_h_difficulty
        elif self.team_a.unique_id == team_id:
            return self.team_a_difficulty
        else:
            raise ValueError(
                f"Team '{team}' not in fixture, '{str(self)}'")

    def is_home(self, team: Union[int, Team]) -> bool:
        """Determines whether team passed is at home or away.

        Parameters
        ----------
        team : Union[int, Team]
            Team to find home or away for.

        Returns
        -------
        bool
            True if home, False otherwise.

        Raises
        ------
        ValueError
            If `team` is not in fixture.
        """
        if isinstance(team, Team):
            team_id = team.unique_id
        else:
            team_id = team

        if self.team_h.unique_id == team_id:
            return True
        elif self.team_a.unique_id == team_id:
            return False
        else:
            raise ValueError(
                f"Team '{team}' not in fixture, '{str(self)}'")

    '''@classmethod
    def group_fixtures_by_gameweek(cls, fixtures: ElementGroup[Fixture]) -> dict[Event, ElementGroup[Fixture]]:
        """Groups an ElementGroup of fixtures by gameweek.

        Parameters
        ----------
        fixtures : ElementGroup[fixture]
            Fixtures to group.

        Returns
        -------
        dict[Event, ElementGroup[fixture]]
            The key is the event, the value is the fixtures in that gameweek.
        """
        return super().group_fixtures_by_gameweek(fixtures)'''


def get_players(*, team: str = "All", position: str = "All", sort_by: str = "Total Points") -> pd.DataFrame:
    if team == "All":
        teams_found = Team.get()
    else:
        teams_found = Team.get(name=team)

    if position == "All":
        positions_found = Position.get()
    else:
        positions_found = Position.get(singular_name=position)

    players_found = Player.get(element_type=tuple(
        positions_found), team=tuple(teams_found))

    label = Label.get(label=sort_by)[0]
    players_sorted = players_found.sort(label.name)

    df = players_sorted.to_df("element_type", label.name)
    df["player"] = players_sorted
    df["team"] = [player.team for player in players_sorted]
    df = df[["player", "team", "element_type", label.name]]

    return df


def get_fixtures(*, event: str = "All", team: str = "All", sort_by: str = "kickoff_time") -> pd.DataFrame:
    if event == "All":
        events_found = Event.get()
    else:
        event_name = event.split(" - ")[0]
        events_found = Event.get(name=event_name)

    fixtures_found = Fixture.get(event=tuple(events_found))
    if team != "All":
        team_obj = Team.get(name=team)[0]
        fixtures_found = fixtures_found.filter(
            method_="or", team_h=team_obj, team_a=team_obj)

    if sort_by == "kickoff_time":
        reverse_ = False
    else:
        reverse_ = True

    # label = fpld.Label.get(label=sort_by_name)[0]
    fixtures_sorted = fixtures_found.sort(sort_by, reverse=reverse_)
    df = fixtures_sorted.to_df("score", "event", sort_by)

    if sort_by == "kickoff_time":
        df["kickoff_time"] = df["kickoff_time"].apply(
            lambda date_: datetime_to_string(date_))

    return df


def get_events() -> pd.DataFrame:
    df = Event.get_all().to_df("name", "deadline_time",
                               "most_selected", "most_transferred_in", "most_captained",
                               "most_vice_captained", "finished")
    df["deadline_time"] = df["deadline_time"].apply(
        lambda date_: datetime_to_string(date_))

    return df

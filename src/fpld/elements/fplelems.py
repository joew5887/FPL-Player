from __future__ import annotations
import math
from typing import TypeVar, Any, Union, Optional
from ..constants import URLS
from ..util.percent import percent
from ..util import API
from .team import BaseTeam
from .player import BasePlayer, BasePlayerFull, BasePlayerHistory, BasePlayerHistoryPast
from .fixture import BaseFixture
from .event import BaseEvent
from .position import Position
from dataclasses import Field, dataclass, field
from ..util.attribute import CategoricalVar
from .element import ElementGroup


team = TypeVar("team", bound="Team")
player = TypeVar("player", bound="Player")
event = TypeVar("event", bound="Event")
fixture = TypeVar("fixture", bound="Fixture")


@dataclass(frozen=True, order=True, kw_only=True)
class Team(BaseTeam[team]):
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
        score = 0
        multiplier = 0.9

        for i, fixtures in enumerate(all_fixtures_by_event.values()):
            fixture: Fixture
            for fixture in fixtures:
                diff = fixture.get_difficulty(self)

                score += diff * multiplier
                multiplier = math.e ** (-0.4 * i)

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

    def get_all_fixtures(self) -> ElementGroup[fixture]:
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

    def player_total(self, *cols: tuple[str], by_position: Position = None) -> Union[float, int]:
        """Total points for all the players in a team, for a given attribute.

        Parameters
        ----------
        by_position : Position, optional
            Position to filter, None means all positions, by default None

        Returns
        -------
        Union[float, int]
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
        """Total goal contributions for a team.

        Parameters
        ----------
        by_position : Position, optional
            Position to filter, None means all positions, by default None

        Returns
        -------
        int
            Total goals + total assists.
        """
        cols = ["goals_scored", "assists"]

        return self.player_total(*cols, by_position=by_position)


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
class PlayerHistoryPast(BasePlayerHistoryPast):
    pass


class PlayerFull(BasePlayerFull[PlayerHistory, PlayerHistoryPast]):
    """Game by game, season by season data for a player, linked to other FPL elements.
    """

    def __init__(self, history: PlayerHistory, history_past: PlayerHistoryPast):
        self._history = history
        self._history_past = history_past

    @classmethod
    def from_id(cls, player_id: int) -> PlayerFull:
        """Takes a player ID, and returns full data for that player

        Parameters
        ----------
        player_id : int
            Player ID to get stats for.

        Returns
        -------
        PlayerFull
           Player stats, game by game, season by season.
        """
        url = URLS["ELEMENT-SUMMARY"].format(player_id)
        api = API(url)  # Need to have offline feature
        history = PlayerHistory.from_api(api.data["history"])
        history_past = PlayerHistoryPast.from_api(api.data["history_past"])
        return PlayerFull(history, history_past)


@dataclass(frozen=True, order=True, kw_only=True)
class Player(BasePlayer[player]):
    """Player element, linked to other FPL elements.
    """
    team: Team = field(hash=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

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
        return percent(self.goal_contributions, position_total)

    @property
    def percent_team(self) -> float:
        """Percent of player  contributions to total team contributions.

        Returns
        -------
        float
            player contributions / team contributions.
        """
        team_total = self.team.total_goal_contributions()
        return percent(self.goal_contributions, team_total)

    def in_full(self) -> PlayerFull:
        """Game by game, season by season data for a player.

        Returns
        -------
        PlayerFull
            Game by game, season by season data for a player.
        """
        return PlayerFull.from_id(self.id)


@dataclass(frozen=True, order=True, kw_only=True)
class Event(BaseEvent[event]):
    """Event / gameweek element, linked to other FPL elements.
    """
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
        """Get all fixtures / results from a gameweek.

        Returns
        -------
        ElementGroup[Fixture]
            Unordered list of fixtures in gameweek.
        """
        return Fixture.get(event=self)


@dataclass(frozen=True, order=True, kw_only=True)
class Fixture(BaseFixture[fixture]):
    """Fixture / result element, linked to other FPL elements.
    """
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

    def get_difficulty(self, team: Union[int, Team], raise_value_error: bool = True) -> Optional[int]:
        """Gets the difficulty of a fixture for a team.

        Parameters
        ----------
        team : Union[int, Team]
            Team to find difficulty for.
        raise_value_error : bool, optional
            True raises a 'ValueError', False returns None, by default True

        Returns
        -------
        Optional[int]
            Difficulty of the game for `team`. 

        Raises
        ------
        ValueError
            If `team` is not in fixture and `raise_value_error` is True.
        """
        if isinstance(team, Team):
            team_id = team.unique_id
        else:
            team_id = team

        if self.team_h.unique_id == team_id:
            return self.team_h_difficulty
        if self.team_a.unique_id == team_id:
            return self.team_a_difficulty

        if raise_value_error:
            raise ValueError(
                f"Team ID '{team}' not in fixture, '{str(self)}'")

        return None

    @classmethod
    def group_fixtures_by_gameweek(cls, fixtures: ElementGroup[fixture]) -> dict[Event, ElementGroup[fixture]]:
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
        return super().group_fixtures_by_gameweek(fixtures)

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import Field, dataclass, field, fields
from datetime import datetime
from ..util.attribute import CategoricalVar, ContinuousVar
from .element import Element, ElementGroup
from typing import Optional, TypeVar, Generic, Any, get_type_hints
from ..util import API
from ..constants import URLS
from .position import Position


base_player = TypeVar("base_player", bound="BasePlayer")
playerfull = TypeVar("playerfull")
player_history = TypeVar("player_history")
player_history_past = TypeVar("player_history_past")


@dataclass(frozen=True, order=True, kw_only=True)
class BasePlayer(Element[base_player], Generic[base_player]):
    """Player element, unlinked from other FPL elements.
    """
    _ATTR_FOR_STR = "web_name"

    chance_of_playing_next_round: Optional[int] = field(hash=False, repr=False)
    chance_of_playing_this_round: Optional[int] = field(hash=False, repr=False)
    code: int = field(repr=False)
    cost_change_event: int = field(hash=False, repr=False)
    cost_change_event_fall: int = field(hash=False, repr=False)
    cost_change_start: int = field(hash=False, repr=False)
    cost_change_start_fall: int = field(hash=False, repr=False)
    dreamteam_count: int = field(hash=False, repr=False)
    element_type: Position = field(hash=False)
    ep_next: float = field(hash=False, repr=False)
    ep_this: float = field(hash=False, repr=False)
    event_points: int = field(hash=False, repr=False)
    first_name: str = field(hash=False, repr=False)
    form: float = field(hash=False, repr=False)
    id: int = field(compare=True)
    in_dreamteam: bool = field(hash=False, repr=False)
    news: str = field(hash=False, repr=False)
    news_added: str = field(hash=False, repr=False)
    now_cost: int = field(hash=False)
    photo: str = field(hash=False, repr=False)
    points_per_game: float = field(hash=False, repr=False)
    second_name: str = field(hash=False, repr=False)
    selected_by_percent: float = field(hash=False, repr=False)
    special: bool = field(hash=False, repr=False)
    squad_number: Optional[int] = field(hash=False, repr=False)
    status: str = field(hash=False, repr=False)
    team: int = field(hash=False)
    team_code: int = field(hash=False, repr=False)
    total_points: int = field(hash=False, repr=False)
    transfers_in: int = field(hash=False, repr=False)
    transfers_in_event: int = field(hash=False, repr=False)
    transfers_out: int = field(hash=False, repr=False)
    transfers_out_event: int = field(hash=False, repr=False)
    value_form: float = field(hash=False, repr=False)
    value_season: float = field(hash=False, repr=False)
    web_name: str = field(hash=False)  # foo
    minutes: int = field(hash=False, repr=False)
    goals_scored: int = field(hash=False, repr=False)
    assists: int = field(hash=False, repr=False)
    clean_sheets: int = field(hash=False, repr=False)
    goals_conceded: int = field(hash=False, repr=False)
    own_goals: int = field(hash=False, repr=False)
    penalties_saved: int = field(hash=False, repr=False)
    penalties_missed: int = field(hash=False, repr=False)
    yellow_cards: int = field(hash=False, repr=False)
    red_cards: int = field(hash=False, repr=False)
    saves: int = field(hash=False, repr=False)
    bonus: int = field(hash=False, repr=False)
    bps: int = field(hash=False, repr=False)
    influence: float = field(hash=False, repr=False)
    creativity: float = field(hash=False, repr=False)
    threat: float = field(hash=False, repr=False)
    ict_index: float = field(hash=False, repr=False)
    influence_rank: int = field(hash=False, repr=False)
    influence_rank_type: int = field(hash=False, repr=False)
    creativity_rank: int = field(hash=False, repr=False)
    creativity_rank_type: int = field(hash=False, repr=False)
    threat_rank: int = field(hash=False, repr=False)
    threat_rank_type: int = field(hash=False, repr=False)
    ict_index_rank: int = field(hash=False, repr=False)
    ict_index_rank_type: int = field(hash=False, repr=False)
    corners_and_indirect_freekicks_order: Optional[int] = field(
        hash=False, repr=False)
    corners_and_indirect_freekicks_text: str = field(hash=False, repr=False)
    direct_freekicks_order: Optional[int] = field(hash=False, repr=False)
    direct_freekicks_text: str = field(hash=False, repr=False)
    penalties_order: Optional[int] = field(hash=False, repr=False)
    penalties_text: str = field(hash=False, repr=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["element_type"] = Position.get_by_id(
            new_instance["element_type"])

        return new_instance

    @ property
    def ppm(self) -> float:
        """Points per million cost.

        Returns
        -------
        float
            The higher, the more points for the cost.
        """
        return self.total_points / self.now_cost

    @property
    def goal_contributions(self) -> int:
        """Total goal contributions.

        Returns
        -------
        int
            goals + assists
        """
        return self.goals_scored + self.assists

    @ property
    def transfer_diff(self) -> int:
        """Difference between transfers in and transfers out for current event.

        Returns
        -------
        int
            transfers_in - transfers_out
        """
        return self.transfers_in_event - self.transfers_out_event

    def in_full(self) -> BasePlayerFull:
        """Game by game, season by season data for a player.

        Returns
        -------
        BasePlayerFull
            Game by game, season by season data for a player.
        """
        return BasePlayerFull.from_id(self.id)

    @ classmethod
    @ property
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @ classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        return api.data["elements"]


class BasePlayerFull(Generic[player_history, player_history_past]):
    """Game by game, season by season data for a player, unlinked from other FPL elements.
    """

    def __init__(self, history: player_history, history_past: player_history_past):
        self._history = history
        self._history_past = history_past

    @property
    def history(self) -> player_history:
        """Player stats this season.

        Returns
        -------
        player_history
            Player stats this season.
        """
        return self._history

    @property
    def history_past(self) -> player_history_past:
        """Player stats, season by season.

        Returns
        -------
        player_history_past
            Player stats, season by season.
        """
        return self._history_past

    @classmethod
    def from_id(cls, player_id: int) -> BasePlayerFull:
        """Takes a player ID, and returns full data for that player

        Parameters
        ----------
        player_id : int
            Player ID to get stats for.

        Returns
        -------
        BasePlayerFull
           Player stats, game by game, season by season.
        """
        url = URLS["ELEMENT-SUMMARY"].format(player_id)
        api = API(url)  # Need to have offline feature
        history = BasePlayerHistory.from_api(api.data["history"])
        history_past = BasePlayerHistoryPast.from_api(
            api.data["history_past"])
        return BasePlayerFull(history, history_past)


@dataclass(frozen=True, kw_only=True)
class BasePlayerStats(ABC):
    @classmethod
    def _edit_stat_from_api(cls, field: Field, attr_list: list[Any]) -> list[Any]:
        """Pre-format API data before passing it into the class.

        Like '__pre__init__()' from 'Element'.

        Parameters
        ----------
        field : Field
            Attribute from class to create.
        attr_list : list[Any]
            Attribute values for `field`.

        Returns
        -------
        list[Any]
            Formatted `attr_list`.
        """
        return attr_list

    @classmethod
    def from_api(cls, api_data: list[dict[str, Any]]) -> BasePlayerStats:
        """Converts data from API to a `BasePlayerStats` object.

        Parameters
        ----------
        api_data : list[dict[str, Any]]
            API data in JSON form.

        Returns
        -------
        BasePlayerStats
            Object containing `api_data`.
        """
        stat_attributes = {}
        resolved_hints = get_type_hints(cls)  # Gets Generic Types for fields.

        for f in cls.all_fields():
            attr_list = []

            for state in api_data:
                # KeyError: 'fixture'.
                attr_list.append(state[f.name])

            attr_list = cls._edit_stat_from_api(f, attr_list)

            stat_attributes[f.name] = resolved_hints[f.name](attr_list, f.name)

        return cls(**stat_attributes)

    @classmethod
    def all_fields(cls) -> list[Field]:
        """All fields for a class.

        Returns
        -------
        list[Field]
            All fields, including names of attributes.
        """
        return list(fields(cls))

    @classmethod
    @property
    def categorical_vars(cls) -> list[str]:
        """All categorical variables.

        Returns
        -------
        list[str]
            E.g. string variables.
        """
        return [f.name for f in cls.all_fields() if "CategoricalVar" in str(f.type)]

    @classmethod
    @property
    def continuous_vars(cls) -> list[str]:
        """All continuous variables.

        Returns
        -------
        list[str]
            E.g. integer and float variables.
        """
        return [f.name for f in cls.all_fields() if "ContinuousVar" in str(f.type)]


@dataclass(frozen=True, kw_only=True)
class BasePlayerHistory(BasePlayerStats):
    """Player history, season by season, unlinked from other FPL elements.
    """
    fixture: CategoricalVar[int] = field(hash=False, repr=False)
    opponent_team: CategoricalVar[int] = field(hash=False, repr=False)
    total_points: ContinuousVar[int] = field(hash=False, repr=False)
    was_home: CategoricalVar[bool] = field(hash=False, repr=False)
    kickoff_time: CategoricalVar[datetime] = field(hash=False, repr=False)
    team_h_score: ContinuousVar[int] = field(hash=False, repr=False)
    team_a_score: ContinuousVar[int] = field(hash=False, repr=False)
    round: CategoricalVar[int] = field(hash=False, repr=False)
    minutes: ContinuousVar[int] = field(hash=False, repr=False)
    goals_scored: ContinuousVar[int] = field(hash=False, repr=False)
    assists: ContinuousVar[int] = field(hash=False, repr=False)
    clean_sheets: ContinuousVar[int] = field(hash=False, repr=False)
    goals_conceded: ContinuousVar[int] = field(hash=False, repr=False)
    own_goals: ContinuousVar[int] = field(hash=False, repr=False)
    penalties_saved: ContinuousVar[int] = field(hash=False, repr=False)
    penalties_missed: ContinuousVar[int] = field(hash=False, repr=False)
    yellow_cards: ContinuousVar[int] = field(hash=False, repr=False)
    red_cards: ContinuousVar[int] = field(hash=False, repr=False)
    saves: ContinuousVar[int] = field(hash=False, repr=False)
    bonus: ContinuousVar[int] = field(hash=False, repr=False)
    bps: ContinuousVar[int] = field(hash=False, repr=False)
    influence: ContinuousVar[float] = field(hash=False, repr=False)
    creativity: ContinuousVar[float] = field(hash=False, repr=False)
    threat: ContinuousVar[float] = field(hash=False, repr=False)
    ict_index: ContinuousVar[float] = field(hash=False, repr=False)
    value: ContinuousVar[int] = field(hash=False, repr=False)
    transfers_balance: ContinuousVar[int] = field(hash=False, repr=False)
    selected: ContinuousVar[int] = field(hash=False, repr=False)
    transfers_in: ContinuousVar[int] = field(hash=False, repr=False)
    transfers_out: ContinuousVar[int] = field(hash=False, repr=False)


@dataclass(frozen=True, kw_only=True)
class BasePlayerHistoryPast(BasePlayerStats):
    season_name: CategoricalVar[str] = field(hash=False, repr=False)
    start_cost: ContinuousVar[int] = field(hash=False, repr=False)
    end_cost: ContinuousVar[int] = field(hash=False, repr=False)
    total_points: ContinuousVar[int] = field(hash=False, repr=False)
    minutes: ContinuousVar[int] = field(hash=False, repr=False)
    goals_scored: ContinuousVar[int] = field(hash=False, repr=False)
    assists: ContinuousVar[int] = field(hash=False, repr=False)
    clean_sheets: ContinuousVar[int] = field(hash=False, repr=False)
    goals_conceded: ContinuousVar[int] = field(hash=False, repr=False)
    own_goals: ContinuousVar[int] = field(hash=False, repr=False)
    penalties_saved: ContinuousVar[int] = field(hash=False, repr=False)
    penalties_missed: ContinuousVar[int] = field(hash=False, repr=False)
    yellow_cards: ContinuousVar[int] = field(hash=False, repr=False)
    red_cards: ContinuousVar[int] = field(hash=False, repr=False)
    saves: ContinuousVar[int] = field(hash=False, repr=False)
    bonus: ContinuousVar[int] = field(hash=False, repr=False)
    bps: ContinuousVar[int] = field(hash=False, repr=False)
    influence: ContinuousVar[float] = field(hash=False, repr=False)
    creativity: ContinuousVar[float] = field(hash=False, repr=False)
    threat: ContinuousVar[float] = field(hash=False, repr=False)
    ict_index: ContinuousVar[float] = field(hash=False, repr=False)

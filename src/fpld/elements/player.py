from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import Field, dataclass, field, fields

from fpld.util.attribute import CategoricalVar
from .element import _Element, ElementGroup
from typing import Optional, Type, TypeVar, Generic, Any, get_type_hints, Iterable
from ..util import API
from ..constants import URLS, round_value
from .playerfull import _PlayerFull, _PlayerHistory, _PlayerHistoryPast


_player = TypeVar("_player", bound="_Player[Any]")


@dataclass(frozen=True, order=True, kw_only=True)
class _Player(_Element[_player], Generic[_player]):
    """Player element, unlinked from other FPL elements.
    """
    _ATTR_FOR_STR = "web_name"

    id: int = field(repr=False)

    chance_of_playing_next_round: Optional[int] = field(
        hash=False, repr=False, compare=False)
    chance_of_playing_this_round: Optional[int] = field(
        hash=False, repr=False, compare=False)
    code: int = field(repr=False, compare=False)
    cost_change_event: int = field(hash=False, repr=False, compare=False)
    cost_change_event_fall: int = field(hash=False, repr=False, compare=False)
    cost_change_start: int = field(hash=False, repr=False, compare=False)
    cost_change_start_fall: int = field(hash=False, repr=False, compare=False)
    dreamteam_count: int = field(hash=False, repr=False, compare=False)
    element_type: Any = field(hash=False, compare=False)
    ep_next: float = field(hash=False, repr=False, compare=False)
    ep_this: float = field(hash=False, repr=False, compare=False)
    event_points: int = field(hash=False, repr=False, compare=False)
    first_name: str = field(hash=False, repr=False, compare=False)
    form: float = field(hash=False, repr=False, compare=False)
    in_dreamteam: bool = field(hash=False, repr=False, compare=False)
    news: str = field(hash=False, repr=False, compare=False)
    news_added: str = field(hash=False, repr=False, compare=False)
    now_cost: int = field(hash=False, repr=False, compare=False)
    photo: str = field(hash=False, repr=False, compare=False)
    points_per_game: float = field(hash=False, repr=False, compare=False)
    second_name: str = field(hash=False, repr=False, compare=False)
    selected_by_percent: float = field(hash=False, repr=False, compare=False)
    special: bool = field(hash=False, repr=False, compare=False)
    squad_number: Optional[int] = field(hash=False, repr=False, compare=False)
    status: str = field(hash=False, repr=False, compare=False)
    team: Any = field(hash=False, compare=False)
    team_code: int = field(hash=False, repr=False, compare=False)
    total_points: int = field(hash=False, repr=False, compare=False)
    transfers_in: int = field(hash=False, repr=False, compare=False)
    transfers_in_event: int = field(hash=False, repr=False, compare=False)
    transfers_out: int = field(hash=False, repr=False, compare=False)
    transfers_out_event: int = field(hash=False, repr=False, compare=False)
    value_form: float = field(hash=False, repr=False, compare=False)
    value_season: float = field(hash=False, repr=False, compare=False)
    web_name: str = field(hash=False, compare=False)  # foo
    minutes: int = field(hash=False, repr=False, compare=False)
    goals_scored: int = field(hash=False, repr=False, compare=False)
    assists: int = field(hash=False, repr=False, compare=False)
    clean_sheets: int = field(hash=False, repr=False, compare=False)
    goals_conceded: int = field(hash=False, repr=False, compare=False)
    own_goals: int = field(hash=False, repr=False, compare=False)
    penalties_saved: int = field(hash=False, repr=False, compare=False)
    penalties_missed: int = field(hash=False, repr=False, compare=False)
    yellow_cards: int = field(hash=False, repr=False, compare=False)
    red_cards: int = field(hash=False, repr=False, compare=False)
    saves: int = field(hash=False, repr=False, compare=False)
    bonus: int = field(hash=False, repr=False, compare=False)
    bps: int = field(hash=False, repr=False, compare=False)
    influence: float = field(hash=False, repr=False, compare=False)
    creativity: float = field(hash=False, repr=False, compare=False)
    threat: float = field(hash=False, repr=False, compare=False)
    ict_index: float = field(hash=False, repr=False, compare=False)
    influence_rank: int = field(hash=False, repr=False, compare=False)
    influence_rank_type: int = field(hash=False, repr=False, compare=False)
    creativity_rank: int = field(hash=False, repr=False, compare=False)
    creativity_rank_type: int = field(hash=False, repr=False, compare=False)
    threat_rank: int = field(hash=False, repr=False, compare=False)
    threat_rank_type: int = field(hash=False, repr=False, compare=False)
    ict_index_rank: int = field(hash=False, repr=False, compare=False)
    ict_index_rank_type: int = field(hash=False, repr=False, compare=False)
    corners_and_indirect_freekicks_order: Optional[int] = field(
        hash=False, repr=False, compare=False)
    corners_and_indirect_freekicks_text: str = field(
        hash=False, repr=False, compare=False)
    direct_freekicks_order: Optional[int] = field(
        hash=False, repr=False, compare=False)
    direct_freekicks_text: str = field(hash=False, repr=False, compare=False)
    penalties_order: Optional[int] = field(
        hash=False, repr=False, compare=False)
    penalties_text: str = field(hash=False, repr=False, compare=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["form"] = float(new_instance["form"])

        return new_instance

    @ property
    def ppm(self) -> float:
        """Points per million cost.

        Returns
        -------
        float
            The higher, the more points for the cost.
        """
        return round_value(self.total_points / self.now_cost)

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

    @abstractmethod
    def in_full(self) -> Any:
        """Game by game, season by season data for a player.

        Returns
        -------
        _playerfull
            Game by game, season by season data for a player.
        """
        ...

    @ classmethod
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @ classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = API(cls.api_link())

        data_from_api: list[dict[str, Any]] = api.data["elements"]

        return data_from_api

    @classmethod
    def in_cost_range(
            cls, player_pool: ElementGroup[_player],
            *, lower: int = 0, upper: int = 150, include_boundaries: bool = True) -> ElementGroup[_player]:
        """Filters a group of players based on if their cost lies between two values.

        Parameters
        ----------
        player_pool : ElementGroup[_player]
            Players to filter.
        lower : int, optional
           Lower bound cost, by default 0
        upper : int, optional
            Upper bound cost, by default 150
        include_boundaries : bool, optional
            If upper = 100 and a player costs 100, they will be included, by default True

        Returns
        -------
        ElementGroup[_player]
            Players between `lower` and `upper` costs.
        """

        players_found = []

        for player in player_pool:
            if (lower <= player.now_cost and include_boundaries) or (lower < player.now_cost):
                if (player.now_cost <= upper and include_boundaries) or (player.now_cost < upper):
                    players_found.append(player)

        return ElementGroup[_player](players_found)


@dataclass(frozen=True, order=True, kw_only=True)
class BasePlayer(_Player["BasePlayer"]):
    """Independent Player element, not linked to any other FPL elements.
    """
    team: int = field(hash=False, compare=False)
    element_type: int = field(hash=False, compare=False)

    def in_full(self) -> BasePlayerFull:
        return BasePlayerFull.from_player_id(self.id)


@dataclass(frozen=True, kw_only=True)
class BasePlayerHistory(_PlayerHistory["BasePlayerHistory"]):
    fixture: CategoricalVar[int] = field(hash=False, repr=False)
    opponent_team: CategoricalVar[int] = field(hash=False, repr=False)


@dataclass(frozen=True, kw_only=True)
class BasePlayerHistoryPast(_PlayerHistoryPast["BasePlayerHistoryPast"]):
    pass


class BasePlayerFull(_PlayerFull[BasePlayerHistory, BasePlayerHistoryPast]):
    @classmethod
    def from_player_id(cls, player_id: int) -> BasePlayerFull:
        data = cls.get_api(player_id)

        history = BasePlayerHistory.from_api(data["history"])
        history_past = BasePlayerHistoryPast.from_api(
            data["history_past"])

        return BasePlayerFull(history, history_past)

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import Field, dataclass, field, fields
from datetime import datetime
from fpld.util.attribute import CategoricalVar, ContinuousVar
from .element import Element
from typing import Optional, TypeVar, Generic, Any, get_type_hints
from ..util import API
from ..constants import URLS
from .position import Position


baseplayer = TypeVar("baseplayer", bound="BasePlayer")
playerfull = TypeVar("playerfull")


@dataclass(frozen=True, order=True, kw_only=True)
class BasePlayer(Element[baseplayer], Generic[baseplayer]):
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

    def __str__(self) -> str:
        return self.web_name

    @ property
    def ppm(self) -> float:
        return self.total_points / self.now_cost

    @property
    def goal_contributions(self) -> int:
        return self.goals_scored + self.assists

    @ property
    def transfer_diff(self) -> int:
        return self.transfers_in_event - self.transfers_out_event

    @ classmethod
    @ property
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @ classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        return api.data["elements"]

    def in_full(self) -> BasePlayerFull:
        return BasePlayerFull.from_id(self.id)


class BasePlayerFull:
    def __init__(self, fixtures: BasePlayerFixtures, history: BasePlayerHistory, history_past: BasePlayerHistoryPast):
        self.__fixtures = fixtures
        self.__history = history
        self.__history_past = history_past

    @property
    def fixtures(self) -> BasePlayerFixtures:
        return self.__fixtures

    @property
    def history(self) -> BasePlayerHistory:
        return self.__history

    @property
    def history_past(self) -> BasePlayerHistoryPast:
        return self.__history_past

    @classmethod
    def from_id(cls, player_id: int) -> BasePlayerFull:
        url = URLS["ELEMENT-SUMMARY"].format(player_id)
        api = API(url)  # Need to have offline feature
        fixtures = BasePlayerFixtures.from_api(api.data["fixtures"])
        history = BasePlayerHistory.from_api(api.data["history"])
        history_past = BasePlayerHistoryPast.from_api(api.data["history_past"])
        return BasePlayerFull(fixtures, history, history_past)


@dataclass(frozen=True, kw_only=True)
class BasePlayerStats(ABC):
    @classmethod
    def _edit_stat_from_api(cls, field: Field, attr_list: list[Any]) -> dict[str, list[Any]]:
        return attr_list

    @classmethod
    def from_api(cls, api_data: list[dict[str, Any]]) -> BasePlayerStats:
        stat_attributes = {}
        resolved_hints = get_type_hints(cls)

        for f in cls.all_fields():
            attr_list = []

            for state in api_data:
                attr_list.append(state[f.name])

            attr_list = cls._edit_stat_from_api(f, attr_list)

            stat_attributes[f.name] = resolved_hints[f.name](attr_list, f.name)

        return cls(**stat_attributes)

    @classmethod
    def all_fields(cls) -> list[Field]:
        return list(fields(cls))

    @classmethod
    @property
    def categorical_vars(cls) -> list[str]:
        return [f.name for f in cls.all_fields() if "CategoricalVar" in str(f.type)]

    @classmethod
    @property
    def continuous_vars(cls) -> list[str]:
        return [f.name for f in cls.all_fields() if "ContinuousVar" in str(f.type)]


@dataclass(frozen=True, kw_only=True)
class BasePlayerFixtures(BasePlayerStats):
    fixture: CategoricalVar[int] = field(hash=False, repr=False)


@dataclass(frozen=True, kw_only=True)
class BasePlayerHistory(BasePlayerStats):
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

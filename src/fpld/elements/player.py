from dataclasses import dataclass, field
from .element import Element
from typing import Optional, TypeVar, Generic, Any
from ..util import API
from ..constants import API_URL
from .position import Position


baseplayer = TypeVar("baseplayer", bound="BasePlayer")


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
        return API_URL + "bootstrap-static/"

    @ classmethod
    @ property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data["elements"]

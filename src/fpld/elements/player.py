from abc import ABC, abstractmethod
from .element import Element
from typing import Optional, TypeVar, Generic
from ..util import API_URL, API, STR_TO_DATETIME
from datetime import datetime


baseplayer = TypeVar("baseplayer", bound="BasePlayer")


class BasePlayer(Element[baseplayer], Generic[baseplayer]):
    chance_of_playing_next_round: Optional[int]
    chance_of_playing_this_round: Optional[int]
    code: int
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    dreamteam_count: int
    element_type: int
    ep_next: float
    ep_this: float
    event_points: int
    first_name: str
    form: float
    id: int
    in_dreamteam: bool
    news: str
    news_added: datetime
    now_cost: int
    photo: str
    points_per_game: float
    second_name: str
    selected_by_percent: float
    special: bool
    squad_number: Optional[int]
    status: str
    team: int
    team_code: int
    total_points: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int
    value_form: float
    value_season: float
    web_name: str  # foo
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: float
    creativity: float
    threat: float
    ict_index: float
    influence_rank: int
    influence_rank_type: int
    creativity_rank: int
    creativity_rank_type: int
    threat_rank: int
    threat_rank_type: int
    ict_index_rank: int
    ict_index_rank_type: int
    corners_and_indirect_freekicks_order: Optional[int]
    corners_and_indirect_freekicks_text: str
    direct_freekicks_order: Optional[int]
    direct_freekicks_text: str
    penalties_order: Optional[int]
    penalties_text: str

    def __init__(self, **attr_to_value):
        """news_added = attr_to_value["news_added"]
        attr_to_value["news_added"] = datetime.strptime(
            news_added, STR_TO_DATETIME)"""
        attr_to_value["selected_by_percent"] = \
            float(attr_to_value["selected_by_percent"])
        super().__init__(**attr_to_value)

    def __str__(self) -> str:
        return f"{self.web_name}"

    def __repr__(self) -> str:
        return f"{self.web_name}"
        return (
            f"Player(id='{self.unique_id}', "
            f"web_name='{self.web_name}', team='{self.team}')"
        )

    @ property
    def ppm(self) -> float:
        raise NotImplementedError
        return self.total_points / self.now_cost

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

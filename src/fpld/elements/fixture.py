from typing import Generic, TypeVar
from .element import Element
from ..util import API_URL, API, STR_TO_DATETIME
from datetime import datetime


basefixture = TypeVar("basefixture", bound="BaseFixture")


class BaseFixture(Element[basefixture], Generic[basefixture]):
    code: int
    event: int
    finished: bool
    finished_provisional: bool
    id: int
    kickoff_time: datetime
    minutes: int
    provisional_start_time: bool
    started: bool
    team_a: int
    team_a_score: int
    team_h: int
    team_h_score: int
    stats: list[dict]
    team_h_difficulty: int
    team_a_difficulty: int
    pulse_id: int

    def __init__(self, **col_to_attr):
        kickoff_time = col_to_attr["kickoff_time"]
        col_to_attr["kickoff_time"] = datetime.strptime(
            kickoff_time, STR_TO_DATETIME)
        super().__init__(**col_to_attr)

    @classmethod
    @property
    def api_link(cls) -> str:
        return API_URL + "fixtures/"

    @classmethod
    @property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data

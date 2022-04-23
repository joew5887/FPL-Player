from typing import TypeVar, Generic
from .element import Element
from ..util import API_URL, API


baseteam = TypeVar("baseteam", bound="BaseTeam")


class BaseTeam(Element[baseteam], Generic[baseteam]):
    code: int
    draw: int
    form: None
    id: int
    loss: int
    name: str
    played: int
    points: int
    position: int
    short_name: str
    strength: int
    team_division: None
    unavailable: bool
    win: int
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int
    pulse_id: int

    @classmethod
    @property
    def api_link(cls) -> str:
        return API_URL + "bootstrap-static/"

    @classmethod
    @property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data["teams"]

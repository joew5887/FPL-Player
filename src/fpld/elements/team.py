from typing import TypeVar, Generic
from .element import Element
from ..util import API
from ..constants import API_URL
from dataclasses import dataclass, field


baseteam = TypeVar("baseteam", bound="BaseTeam")


@dataclass(frozen=True, order=True, kw_only=True)
class BaseTeam(Element[baseteam], Generic[baseteam]):
    code: int = field(repr=False)
    draw: int = field(hash=False, repr=False)
    form: None = field(hash=False, repr=False)
    id: int = field(compare=True)
    loss: int = field(hash=False, repr=False)
    name: str = field(hash=False)
    played: int = field(hash=False, repr=False)
    points: int = field(hash=False, repr=False)
    position: int = field(hash=False, repr=False)
    short_name: str = field(hash=False)
    strength: int = field(hash=False, repr=False)
    team_division: None = field(hash=False, repr=False)
    unavailable: bool = field(hash=False, repr=False)
    win: int = field(hash=False, repr=False)
    strength_overall_home: int = field(hash=False, repr=False)
    strength_overall_away: int = field(hash=False, repr=False)
    strength_attack_home: int = field(hash=False, repr=False)
    strength_attack_away: int = field(hash=False, repr=False)
    strength_defence_home: int = field(hash=False, repr=False)
    strength_defence_away: int = field(hash=False, repr=False)
    pulse_id: int = field(repr=False)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @property
    def api_link(cls) -> str:
        return API_URL + "bootstrap-static/"

    @classmethod
    @property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data["teams"]

    @classmethod
    def get_all_names(cls) -> list[str]:
        all_teams = cls.get()
        return [team.name for team in all_teams]

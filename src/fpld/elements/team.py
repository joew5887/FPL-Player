from typing import TypeVar, Generic, Any
from .element import Element, ElementGroup
from ..util import API
from ..constants import URLS
from dataclasses import dataclass, field


base_team = TypeVar("base_team", bound="BaseTeam")


@dataclass(frozen=True, order=True, kw_only=True)
class BaseTeam(Element[base_team], Generic[base_team]):
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

    @classmethod
    @property
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        return api.data["teams"]

    @classmethod
    def get_all_names(cls) -> list[str]:
        all_teams = cls.get()
        return [team.name for team in all_teams]

    @classmethod
    def gui_get(cls, team_name: str) -> ElementGroup[base_team]:
        if team_name == "All":
            return cls.get()

        return cls.get(name=team_name)

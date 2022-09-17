from typing import TypeVar, Generic, Any
from .element import _Element
from ..util import API
from ..constants import URLS
from dataclasses import dataclass, field


base_team = TypeVar("base_team", bound="BaseTeam")


@dataclass(frozen=True, order=True, kw_only=True)
class BaseTeam(_Element[base_team], Generic[base_team]):
    """Element for team in the Premier League, unlinked from other FPL elements.
    """
    id: int = field()
    code: int = field(repr=False)

    draw: int = field(hash=False, repr=False, compare=False)
    form: None = field(hash=False, repr=False, compare=False)
    loss: int = field(hash=False, repr=False, compare=False)
    name: str = field(hash=False, compare=False)
    played: int = field(hash=False, repr=False, compare=False)
    points: int = field(hash=False, repr=False, compare=False)
    position: int = field(hash=False, repr=False, compare=False)
    short_name: str = field(hash=False, compare=False)
    strength: int = field(hash=False, repr=False, compare=False)
    team_division: None = field(hash=False, repr=False, compare=False)
    unavailable: bool = field(hash=False, repr=False, compare=False)
    win: int = field(hash=False, repr=False, compare=False)
    strength_overall_home: int = field(hash=False, repr=False, compare=False)
    strength_overall_away: int = field(hash=False, repr=False, compare=False)
    strength_attack_home: int = field(hash=False, repr=False, compare=False)
    strength_attack_away: int = field(hash=False, repr=False, compare=False)
    strength_defence_home: int = field(hash=False, repr=False, compare=False)
    strength_defence_away: int = field(hash=False, repr=False, compare=False)
    pulse_id: int = field(repr=False, compare=False)

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
        """All team names in the Premier League.

        Returns
        -------
        list[str]
            E.g. ['Arsenal', 'Aston Villa', ...]
        """
        all_teams = cls.get()

        return all_teams.to_string_list()

    '''@classmethod
    def gui_get(cls, team_name: str) -> ElementGroup[base_team]:
        if team_name == "All":
            return cls.get()

        return cls.get(name=team_name)'''

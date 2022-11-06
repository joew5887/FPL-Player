from typing import TypeVar, Generic, Any
from .element import _Element
from ..util import API
from ..constants import URLS
from dataclasses import dataclass, field


_team = TypeVar("_team", bound="BaseTeam[Any]")


@dataclass(frozen=True, order=True, kw_only=True)
class BaseTeam(_Element[_team], Generic[_team]):
    """Element for team in the Premier League, unlinked from other FPL elements.
    """
    id: int = field(repr=False)
    code: int = field(repr=False)

    draw: int = field(hash=False, repr=False, compare=False)
    form: None = field(hash=False, repr=False, compare=False)
    loss: int = field(hash=False, repr=False, compare=False)
    name: str = field(hash=False, compare=False)
    played: int = field(hash=False, repr=False, compare=False)
    points: int = field(hash=False, repr=False, compare=False)
    position: int = field(hash=False, repr=False, compare=False)
    short_name: str = field(hash=False, repr=False, compare=False)
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
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = API(cls.api_link())

        data_from_api: list[dict[str, Any]] = api.data["teams"]

        return data_from_api

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

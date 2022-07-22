from typing import Generic, TypeVar, Any
from .element import Element, ElementGroup
from ..util import API
from ..constants import URLS, str_to_datetime
from datetime import datetime
from dataclasses import dataclass, field


basefixture = TypeVar("basefixture", bound="BaseFixture")


@dataclass(frozen=True, order=True, kw_only=True)
class BaseFixture(Element[basefixture], Generic[basefixture]):
    _DEFAULT_NAME = None

    code: int = field(repr=False)
    event: int = field(hash=False)
    finished: bool = field(hash=False, repr=False)
    finished_provisional: bool = field(hash=False, repr=False)
    id: int = field(compare=True)
    kickoff_time: datetime = field(hash=False, repr=False)
    minutes: int = field(hash=False, repr=False)
    provisional_start_time: bool = field(hash=False, repr=False)
    started: bool = field(hash=False, repr=False)
    team_a: int = field(hash=False)
    team_a_score: int = field(hash=False, repr=False)
    team_h: int = field(hash=False)
    team_h_score: int = field(hash=False, repr=False)
    stats: list[dict] = field(hash=False, repr=False)
    team_h_difficulty: int = field(hash=False, repr=False)
    team_a_difficulty: int = field(hash=False, repr=False)
    pulse_id: int = field(repr=False)

    def __str__(self) -> str:
        return f"{self.team_h} ({self.team_h_score}) v {self.team_a} ({self.team_a_score})"

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        new_instance["kickoff_time"] = \
            str_to_datetime(new_instance["kickoff_time"])

        return new_instance

    @property
    def desc(self) -> str:
        return f"{self.team_h} v {self.team_a}"

    @property
    def total_goals(self) -> int:
        return self.team_h_score + self.team_a_score

    @classmethod
    @property
    def api_link(cls) -> str:
        return URLS["FIXTURES"]

    @classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        return api.data

    @classmethod
    def get_team_fixtures(cls, team: int) -> ElementGroup[basefixture]:
        home_fixtures = cls.get(team_a=team)
        away_fixtures = cls.get(team_h=team)

        team_fixtures = home_fixtures + away_fixtures

        return team_fixtures.sort("kickoff_time", reverse=False)

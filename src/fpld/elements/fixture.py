from typing import Generic, Optional, TypeVar, Any
from .element import _Element, ElementGroup
from ..util import API
from ..constants import URLS, string_to_datetime
from datetime import datetime
from dataclasses import dataclass, field


_fixture = TypeVar("_fixture", bound="_Fixture[Any]")


@dataclass(frozen=True, order=True, kw_only=True)
class _Fixture(_Element[_fixture], Generic[_fixture]):
    """Fixture / result element, unlinked from other FPL elements.
    """

    kickoff_time: datetime = field(hash=False, repr=False)
    id: int = field(repr=False)

    event: Any = field(hash=False, compare=False)
    code: int = field(repr=False, compare=False)
    finished: bool = field(hash=False, repr=False, compare=False)
    finished_provisional: bool = field(hash=False, repr=False, compare=False)
    minutes: int = field(hash=False, repr=False, compare=False)
    provisional_start_time: bool = field(hash=False, repr=False, compare=False)
    started: bool = field(hash=False, repr=False, compare=False)
    team_a: Any = field(hash=False, compare=False)
    team_a_score: Optional[int] = field(hash=False, repr=False, compare=False)
    team_h: Any = field(hash=False, compare=False)
    team_h_score: Optional[int] = field(hash=False, repr=False, compare=False)
    stats: list[dict[str, Any]] = field(hash=False, repr=False, compare=False)
    team_h_difficulty: int = field(hash=False, repr=False, compare=False)
    team_a_difficulty: int = field(hash=False, repr=False, compare=False)
    pulse_id: int = field(repr=False, compare=False)

    def __str__(self) -> str:
        return f"{self.team_h} v {self.team_a}"

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        if new_instance["kickoff_time"] is None:
            new_instance["kickoff_time"] = datetime.max
            new_instance["event"] = 0
        else:
            new_instance["kickoff_time"] = \
                string_to_datetime(new_instance["kickoff_time"])

        return new_instance

    @property
    def score(self) -> str:
        """`str(fixture)` but scores are added.

        Returns
        -------
        str
            In form: 'Spurs (1) v Wolves (0)'.
        """
        # If game has not happened yet.
        if self.kickoff_time > datetime.now() or self.kickoff_time == datetime.min:
            return f"{self.team_h} v {self.team_a}"

        return f"({self.team_h}) {self.team_h_score} - {self.team_a_score} ({self.team_a})"

    @property
    def total_goals(self) -> Optional[int]:
        """Total goals scored in a game.

        Returns
        -------
        int
            Total goals scored in a game.
        """

        if self.team_a_score is None or self.team_h_score is None:
            return None

        return self.team_h_score + self.team_a_score

    @ classmethod
    def api_link(cls) -> str:
        return URLS["FIXTURES"]

    @ classmethod
    def get_all_team_fixtures(cls, team_id: int) -> ElementGroup[_fixture]:
        """Gets all fixtures and results for a team.

        Parameters
        ----------
        team : int
            ID of team to find fixtures for.

        Returns
        -------
        ElementGroup[_fixture]
            All fixtures and results a team has.
        """
        team_games = cls.get(method_="or", team_h=team_id, team_a=team_id)

        return team_games

    @ classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = API(cls.api_link())

        data_from_api: list[dict[str, Any]] = api.data

        return data_from_api

    @ classmethod
    def group_fixtures_by_gameweek(cls, fixtures: ElementGroup[_fixture]) -> dict[int, ElementGroup[_fixture]]:
        """Groups an ElementGroup of fixtures by gameweek.

        Parameters
        ----------
        fixtures : ElementGroup[_fixture]
            Fixtures to group.

        Returns
        -------
        dict[int, ElementGroup[_fixture]]
            The key is the event ID, the value is the fixtures in that gameweek.
        """
        return fixtures.group_by("event")

    @ classmethod
    def split_fixtures_by_finished(cls, fixtures: ElementGroup[_fixture]) -> tuple[ElementGroup[_fixture], ElementGroup[_fixture]]:
        """Splits an ElementGroup of fixtures by whether they have finished.

        Parameters
        ----------
        fixtures : ElementGroup[_fixture]
            Fixtures to group.

        Returns
        -------
        tuple[ElementGroup[_fixture], ElementGroup[_fixture]]
            The first group is completed fixtures, the other is incomplete fixtures.
        """
        return fixtures.split(finished=True)

    @ classmethod
    def get_fixtures_in_event(cls, fixtures: ElementGroup[_fixture], event_id: int) -> ElementGroup[_fixture]:
        """Gets fixtures from a gameweek from `fixtures`.

        Parameters
        ----------
        fixtures : ElementGroup[_fixture]
            Fixtures to group.
        event : int
            Event ID to filter by.

        Returns
        -------
        ElementGroup[_fixture]
            All fixtures from `fixtures` that take place in gameweek `event`.
        """
        return fixtures.filter(event=event_id)


@ dataclass(frozen=True, order=True, kw_only=True)
class BaseFixture(_Fixture["BaseFixture"]):
    """Independent Fixture element, not linked to any other FPL elements.
    """
    event: int = field(hash=False, compare=False)
    team_h: int = field(hash=False, compare=False)
    team_a: int = field(hash=False, compare=False)

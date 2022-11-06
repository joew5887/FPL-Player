from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Generic, Any, get_type_hints, Iterable
from ..constants import URLS
from ..util import API
from ..util.attribute import CategoricalVar, ContinuousVar
from dataclasses import Field, dataclass, field, fields
from datetime import datetime


# _playerfull = TypeVar("_playerfull", bound="_PlayerFull[_PlayerHistory, _PlayerHistoryPast]")
_player_history = TypeVar("_player_history", bound="_PlayerHistory[Any]")
_player_history_past = TypeVar(
    "_player_history_past", bound="_PlayerHistoryPast[Any]")
_playerstats = TypeVar("_playerstats", bound="_PlayerStats[Any]")
_playerstatsdataclass = TypeVar("_playerstatsdataclass", bound="_PlayerStatsDataClass[Any]")


class _PlayerStats(ABC, Generic[_playerstats]):
    def __iter__(self) -> Iterable[dict[str, Any]]:
        # In form: {"fixture": 1, "score": 0}, {"fixture": 2, "score": 1}
        elements = []

        for i in range(len(getattr(self, str(type(self).unique_id_col)))):
            elements.append(
                {f.name: getattr(self, f.name).values[i] for f in type(self).all_fields()})

        return iter(elements)

    @classmethod
    def _edit_stat_from_api(cls, field: Field[Any], attr_list: list[Any]) -> list[Any]:
        """Pre-format API data before passing it into the class.

        Like '__pre__init__()' from 'Element'.

        Parameters
        ----------
        field : Field
            Attribute from class to create.
        attr_list : list[Any]
            Attribute values for `field`.

        Returns
        -------
        list[Any]
            Formatted `attr_list`.
        """
        return attr_list

    @classmethod
    def from_api(cls, api_data: list[dict[str, Any]]) -> Any:
        """Converts data from API to a `BasePlayerStats` object.

        Parameters
        ----------
        api_data : list[dict[str, Any]]
            API data in JSON form.

        Returns
        -------
        BasePlayerStats
            Object containing `api_data`.
        """
        stat_attributes = {}
        resolved_hints = get_type_hints(cls)  # Gets Generic Types for fields.

        for f in cls.all_fields():
            attr_list = []

            for state in api_data:
                # KeyError: 'fixture'.
                attr_list.append(state[f.name])

            attr_list = cls._edit_stat_from_api(f, attr_list)

            stat_attributes[f.name] = resolved_hints[f.name](attr_list, f.name)

        return cls(**stat_attributes)

    @classmethod
    def all_fields(cls) -> list[Field[Any]]:
        """All fields for a class.

        Returns
        -------
        list[Field]
            All fields, including names of attributes.
        """
        return list(fields(cls))

    @classmethod
    @property
    def categorical_vars(cls) -> list[str]:
        """All categorical variables.

        Returns
        -------
        list[str]
            E.g. string variables.
        """
        return [f.name for f in cls.all_fields() if "CategoricalVar" in str(f.type)]

    @classmethod
    @property
    def continuous_vars(cls) -> list[str]:
        """All continuous variables.

        Returns
        -------
        list[str]
            E.g. integer and float variables.
        """
        return [f.name for f in cls.all_fields() if "ContinuousVar" in str(f.type)]

    @classmethod
    @property
    @abstractmethod
    def unique_id_col(cls) -> str:
        """The field that identifies each different data entry, e.g. fixture.

        Returns
        -------
        str
            Name of field.
        """
        return ""


class _PlayerStatsDataClass(_PlayerStats[_playerstatsdataclass]):
    @classmethod
    def all_fields(cls) -> list[Field[Any]]:
        return list(fields(cls))


@dataclass(frozen=True, kw_only=True)
class _PlayerHistory(_PlayerStats[_player_history]):
    """Player history, season by season, unlinked from other FPL elements.
    """
    fixture: CategoricalVar[Any] = field(hash=False, repr=False)
    opponent_team: CategoricalVar[Any] = field(hash=False, repr=False)
    total_points: ContinuousVar = field(hash=False, repr=False)
    was_home: CategoricalVar[bool] = field(hash=False, repr=False)
    kickoff_time: CategoricalVar[datetime] = field(hash=False, repr=False)
    team_h_score: ContinuousVar = field(hash=False, repr=False)
    team_a_score: ContinuousVar = field(hash=False, repr=False)
    round: CategoricalVar[int] = field(hash=False, repr=False)
    minutes: ContinuousVar = field(hash=False, repr=False)
    goals_scored: ContinuousVar = field(hash=False, repr=False)
    assists: ContinuousVar = field(hash=False, repr=False)
    clean_sheets: ContinuousVar = field(hash=False, repr=False)
    goals_conceded: ContinuousVar = field(hash=False, repr=False)
    own_goals: ContinuousVar = field(hash=False, repr=False)
    penalties_saved: ContinuousVar = field(hash=False, repr=False)
    penalties_missed: ContinuousVar = field(hash=False, repr=False)
    yellow_cards: ContinuousVar = field(hash=False, repr=False)
    red_cards: ContinuousVar = field(hash=False, repr=False)
    saves: ContinuousVar = field(hash=False, repr=False)
    bonus: ContinuousVar = field(hash=False, repr=False)
    bps: ContinuousVar = field(hash=False, repr=False)
    influence: ContinuousVar = field(hash=False, repr=False)
    creativity: ContinuousVar = field(hash=False, repr=False)
    threat: ContinuousVar = field(hash=False, repr=False)
    ict_index: ContinuousVar = field(hash=False, repr=False)
    value: ContinuousVar = field(hash=False, repr=False)
    transfers_balance: ContinuousVar = field(hash=False, repr=False)
    selected: ContinuousVar = field(hash=False, repr=False)
    transfers_in: ContinuousVar = field(hash=False, repr=False)
    transfers_out: ContinuousVar = field(hash=False, repr=False)

    @classmethod
    @property
    def unique_id_col(cls) -> str:
        return "fixture"


@dataclass(frozen=True, kw_only=True)
class _PlayerHistoryPast(_PlayerStats[_player_history_past]):
    season_name: CategoricalVar[str] = field(hash=False, repr=False)
    start_cost: ContinuousVar = field(hash=False, repr=False)
    end_cost: ContinuousVar = field(hash=False, repr=False)
    total_points: ContinuousVar = field(hash=False, repr=False)
    minutes: ContinuousVar = field(hash=False, repr=False)
    goals_scored: ContinuousVar = field(hash=False, repr=False)
    assists: ContinuousVar = field(hash=False, repr=False)
    clean_sheets: ContinuousVar = field(hash=False, repr=False)
    goals_conceded: ContinuousVar = field(hash=False, repr=False)
    own_goals: ContinuousVar = field(hash=False, repr=False)
    penalties_saved: ContinuousVar = field(hash=False, repr=False)
    penalties_missed: ContinuousVar = field(hash=False, repr=False)
    yellow_cards: ContinuousVar = field(hash=False, repr=False)
    red_cards: ContinuousVar = field(hash=False, repr=False)
    saves: ContinuousVar = field(hash=False, repr=False)
    bonus: ContinuousVar = field(hash=False, repr=False)
    bps: ContinuousVar = field(hash=False, repr=False)
    influence: ContinuousVar = field(hash=False, repr=False)
    creativity: ContinuousVar = field(hash=False, repr=False)
    threat: ContinuousVar = field(hash=False, repr=False)
    ict_index: ContinuousVar = field(hash=False, repr=False)

    @classmethod
    @property
    def unique_id_col(cls) -> str:
        return "season_name"


class _PlayerFull(ABC, Generic[_player_history, _player_history_past]):
    """Game by game, season by season data for a player, unlinked from other FPL elements.
    """

    def __init__(self, history: _player_history, history_past: _player_history_past):
        self.__history = history
        self.__history_past = history_past

    @property
    def history(self) -> _player_history:
        return self.__history

    @property
    def history_past(self) -> _player_history_past:
        return self.__history_past

    @staticmethod
    def get_api(player_id: int) -> dict[str, Any]:
        url = URLS["ELEMENT-SUMMARY"].format(player_id)
        api = API(url)  # Need to have offline feature

        if api.data == "The game is being updated.":
            raise ValueError("The game is being updated.")

        output: dict[str, Any] = api.data

        return output

    @classmethod
    @abstractmethod
    def from_player_id(cls, player_id: int) -> Any: ...

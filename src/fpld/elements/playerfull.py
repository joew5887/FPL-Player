from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
from ..constants import URLS
from ..util import API
import pandas as pd


_player_history = TypeVar("_player_history", bound="_PlayerHistoryDf")
_player_history_past = TypeVar(
    "_player_history_past", bound="_PlayerHistoryPastDf")


class _PlayerStatsDf(ABC, pd.DataFrame):
    @classmethod
    def _edit_stat_from_api(cls, field: str, attr_list: list[Any]) -> list[Any]:
        """Pre-format API data before passing it into the class.

        Like '__pre__init__()' from 'Element'.

        Parameters
        ----------
        field : str
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
        """Converts data from API to a `_PlayerStatsDf` object.

        Parameters
        ----------
        api_data : list[dict[str, Any]]
            API data in JSON form.

        Returns
        -------
        _PlayerStatsDf
            Object containing `api_data`.
        """

        as_df = pd.json_normalize(api_data)

        for col in as_df:
            as_df[col] = cls._edit_stat_from_api(col, list(as_df[col]))

        return cls(as_df)

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


class _PlayerHistoryDf(_PlayerStatsDf):
    @classmethod
    @property
    def unique_id_col(cls) -> str:
        return "fixture"


class _PlayerHistoryPastDf(_PlayerStatsDf):
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
        """Player information, fixture by fixture, for the current season.

        Returns
        -------
        _player_history
            Current season data.
        """
        return self.__history

    @property
    def history_past(self) -> _player_history_past:
        """Player information, season by season, except current season.

        Returns
        -------
        _player_history_past
            Previous season data.
        """
        return self.__history_past

    @staticmethod
    def get_api(player_id: int) -> dict[str, Any]:
        """Get all API data for a player from element summary URL.

        Parameters
        ----------
        player_id : int
            Unique ID of player to get data for.

        Returns
        -------
        dict[str, Any]
            Element summary.

        Raises
        ------
        ValueError
            If the API is being updated, no data can be retrieved from the URL.
        """
        url = URLS["ELEMENT-SUMMARY"].format(player_id)
        api = API(url)  # Need to have offline feature

        if api.data == "The game is being updated.":
            raise ValueError("The game is being updated.")

        output: dict[str, Any] = api.data

        return output

    @classmethod
    @abstractmethod
    def from_player_id(cls, player_id: int) -> Any: ...

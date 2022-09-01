from types import NoneType
from .element import Element, ElementGroup
from datetime import datetime
from typing import Generic, Optional, TypeVar, Union, Any
from ..util import API
from ..constants import URLS, str_to_datetime
from dataclasses import dataclass, field


baseevent = TypeVar("baseevent", bound="BaseEvent")


@dataclass(frozen=True, order=True, kw_only=True)
class BaseEvent(Element[baseevent], Generic[baseevent]):
    """Event / Gameweek element, unlinked from other FPL elements.
    """
    id: int = field(compare=True)
    name: str = field(hash=False)
    deadline_time: datetime = field(hash=False)
    average_entry_score: int = field(hash=False, repr=False)
    finished: bool = field(hash=False, repr=False)
    data_checked: bool = field(hash=False, repr=False)
    highest_scoring_entry: int = field(hash=False, repr=False)
    is_previous: bool = field(hash=False, repr=False)
    is_current: bool = field(hash=False, repr=False)
    is_next: bool = field(hash=False, repr=False)
    cup_leagues_created: bool = field(hash=False, repr=False)
    h2h_ko_matches_created: bool = field(hash=False, repr=False)
    chip_plays: list[dict[str, Union[str, int]]
                     ] = field(hash=False, repr=False)
    most_selected: int = field(hash=False, repr=False)
    most_transferred_in: int = field(hash=False, repr=False)
    top_element: int = field(hash=False, repr=False)
    top_element_info: dict[str, int] = field(hash=False, repr=False)
    transfers_made: int = field(hash=False, repr=False)
    most_captained: int = field(hash=False, repr=False)
    most_vice_captained: int = field(hash=False, repr=False)

    @classmethod
    def __pre_init__(cls, new_instance: dict[str, Any]) -> dict[str, Any]:
        new_instance = super().__pre_init__(new_instance)

        # converts string datetime to datetime object
        new_instance["deadline_time"] = \
            str_to_datetime(new_instance["deadline_time"])

        return new_instance

    def __add__(self, other: int) -> Union[baseevent, NoneType]:
        """Increments the event by `other` gameweeks.

        Parameters
        ----------
        other : int
            Number of gameweeks to go up by.

        Returns
        -------
        Union[baseevent, NoneType]
            Event at gameweek `self.unique_id + other`.
            May be None if outside season.

        Raises
        ------
        NotImplementedError
            `other` must be an int.
        """
        if isinstance(other, int):
            return type(self).get_by_id(self.unique_id + other)

        raise NotImplementedError

    def __iadd__(self, other: int) -> Union[baseevent, NoneType]:
        return self.__add__(other)

    def __sub__(self, other: int) -> Union[baseevent, NoneType]:
        """Decrements the event by `other` gameweeks.

        Parameters
        ----------
        other : int
            Number of gameweeks to go down by.

        Returns
        -------
        Union[baseevent, NoneType]
            Event at gameweek `self.unique_id - other`.
            May be None if outside season.

        Raises
        ------
        NotImplementedError
            `other` must be an int.
        """
        if isinstance(other, int):
            return type(self).get_by_id(self.unique_id - other)

        raise NotImplementedError

    def __isub__(self, other: int) -> Union[baseevent, NoneType]:
        return self.__sub__(other)

    @property
    def started(self) -> bool:
        """Has the gameweek started?

        Uses `datetime.now()`.

        Returns
        -------
        bool
            True if gameweek has started, False otherwise.
        """
        return datetime.now() > self.deadline_time

    @classmethod
    def range(cls, start_gw: baseevent,  start: int, end: int, step: int) -> ElementGroup[baseevent]:
        """Gets a range of events between two points.

        Parameters
        ----------
        start_gw : baseevent
            Event to start list from, may be included in list if `start` = 0.
        start : int
            Where to start incrementing from.
        end : int
            Where to stop incrementing.
        step : int
            How much to increment by.

        Returns
        -------
        ElementGroup[baseevent]
            Events in the range.

        Raises
        ------
        ValueError
            If the range produces an empty list.
        Warning
            If the length of the range is less than the length of events.
            Happens at each end of the season.
        """
        group = [
            start_gw + i for i in range(start, end, step) if start_gw + i is not None]

        if len(group) == 0:
            raise ValueError("No gameweeks found")

        '''if len(group) < len(range(start, end, step)):
            raise Warning("Gameweek range has been cut.")'''

        return ElementGroup[baseevent](group)

    @classmethod
    @property
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @classmethod
    @property
    def previous_gw(cls) -> baseevent:
        """Returns the previous gameweek at the time of program execution.

        Returns
        -------
        baseevent
            The previous gameweek.
        """
        return cls.__find_until_true("is_previous")

    @classmethod
    @property
    def current_gw(cls) -> baseevent:
        """Returns current gameweek at the time of program execution.

        Returns
        -------
        baseevent
            The current gameweek.
        """
        return cls.__find_until_true("is_current")

    @classmethod
    @property
    def next_gw(cls) -> baseevent:
        """Returns the next gameweek at the time of program execution.

        Returns
        -------
        baseevent
            The next gameweek.
        """
        return cls.__find_until_true("is_next")

    @classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        return api.data["events"]

    @classmethod
    def past_and_future(cls) -> tuple[ElementGroup[baseevent], ElementGroup[baseevent]]:
        """Splits all the gameweeks into two groups by whether they have finished.

        Returns
        -------
        tuple[ElementGroup[baseevent], ElementGroup[baseevent]]
            The first group is the completed gameweeks, with the rest in group 2.
        """
        all_events = cls.get_all()

        return all_events.split(finished=True)

    @classmethod
    def __find_until_true(cls, attr: str) -> Optional[baseevent]:
        """Iterates through all gameweeks until the attribute is True.

        Parameters
        ----------
        attr : str
            The boolean attribute to find.

        Returns
        -------
        Optional[baseevent]
            The first gameweek where the attribute is True, may be None if they are all False.
        """
        all_events = cls.get_all()

        for event in all_events:
            if getattr(event, attr):
                return event

        return None

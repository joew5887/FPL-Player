from .element import Element
from datetime import datetime
from typing import Generic, TypeVar, Union
from ..util import API
from ..constants import STR_TO_DATETIME, API_URL


baseevent = TypeVar("baseevent", bound="BaseEvent")


class BaseEvent(Element[baseevent], Generic[baseevent]):
    _DEFAULT_ID = "id"

    id: int
    name: str
    deadline_time: datetime
    average_entry_score: int
    finished: bool
    data_checked: bool
    highest_scoring_entry: int
    is_previous: bool
    is_current: bool
    is_next: bool
    cup_leagues_created: bool
    h2h_ko_matches_created: bool
    chip_plays: list[dict[str, Union[str, int]]]
    most_selected: int
    most_transferred_in: int
    top_element: int
    top_element_info: dict[str, int]
    transfers_made: int
    most_captained: int
    most_vice_captained: int

    def __init__(self, **attr_to_value):
        deadline_time = attr_to_value["deadline_time"]
        attr_to_value["deadline_time"] = datetime.strptime(
            deadline_time, STR_TO_DATETIME)
        super().__init__(**attr_to_value)

    def __str__(self) -> str:
        return f"Gameweek {self.id}"

    def __repr__(self) -> str:
        return (
            f"Event(id='{self.unique_id}', "
            f"deadline='{self.deadline_time}')"
        )

    @property
    def started(self) -> bool: return datetime.now() > self.deadline_time

    @classmethod
    @property
    def api_link(cls) -> str:
        return API_URL + "bootstrap-static/"

    @classmethod
    @property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data["events"]

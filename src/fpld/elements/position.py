from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeVar
from ..util import API
from ..constants import API_URL
from .element import Element


position = TypeVar("position", bound="Position")


@dataclass(frozen=True, order=True, kw_only=True)
class Position(Element[position]):
    _DEFAULT_ID = "id"

    id: int = field(compare=True)
    plural_name: str = field(hash=False, repr=False)
    plural_name_short: str = field(hash=False, repr=False)
    singular_name: str
    singular_name_short: str
    squad_select: int = field(hash=False, repr=False)
    squad_min_play: int = field(hash=False, repr=False)
    squad_max_play: int = field(hash=False, repr=False)
    ui_shirt_specific: bool = field(hash=False, repr=False)
    sub_positions_locked: list = field(hash=False, repr=False)
    element_count: int = field(hash=False, repr=False)

    def __str__(self) -> str:
        return self.singular_name

    @classmethod
    @property
    def api_link(cls) -> str:
        return API_URL + "/bootstrap-static/"

    @classmethod
    @property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data["element_types"]

    @classmethod
    def get_all_names(cls) -> list[str]:
        all_positions = cls.get_from_api()
        return [position.singular_name for position in all_positions]

    @classmethod
    def gui_get(cls, position_name: str) -> list[position]:
        if position_name == "All":
            return cls.get_from_api()

        return cls.get_from_api(singular_name=position_name)

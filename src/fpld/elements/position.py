from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeVar, Any
from ..util import API
from ..constants import URLS
from .element import Element


position = TypeVar("position", bound="Position")


@dataclass(frozen=True, order=True, kw_only=True)
class Position(Element[position]):
    """Position for FPL player. E.g. 'Midfielder'.

    Replaces `player.element_type`.
    """
    _ATTR_FOR_STR = "singular_name"

    id: int = field()

    plural_name: str = field(hash=False, repr=False, compare=False)
    plural_name_short: str = field(hash=False, repr=False, compare=False)
    singular_name: str = field(compare=False)
    singular_name_short: str = field(compare=False)
    squad_select: int = field(hash=False, repr=False, compare=False)
    squad_min_play: int = field(hash=False, repr=False, compare=False)
    squad_max_play: int = field(hash=False, repr=False, compare=False)
    ui_shirt_specific: bool = field(hash=False, repr=False, compare=False)
    sub_positions_locked: list = field(hash=False, repr=False, compare=False)
    element_count: int = field(hash=False, repr=False, compare=False)

    @classmethod
    @property
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        return api.data["element_types"]

    @classmethod
    def get_all_names(cls) -> list[str]:
        """Gets every position and returns their name.

        Returns
        -------
        list[str]
            E.g. ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        """
        all_positions = cls.get()

        return all_positions.to_string_list()

    '''@classmethod
    def gui_get(cls, position_name: str) -> list[position]:
        if position_name == "All":
            return cls.get()

        return cls.get(singular_name=position_name)'''

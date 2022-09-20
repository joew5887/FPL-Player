from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from ..util import API
from ..constants import URLS
from .element import _Element, IDMatchesZeroElements, id_uniqueness_check


@dataclass(frozen=True, order=True, kw_only=True)
class Position(_Element["Position"]):
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
    sub_positions_locked: list[int] = field(hash=False, repr=False, compare=False)
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
    def get_by_name(cls, singular_name_short: str) -> Position:
        position = cls.get(singular_name_short=singular_name_short)

        try:
            id_uniqueness_check(position)
        except IDMatchesZeroElements:
            raise IDMatchesZeroElements(
                f"'{singular_name_short}' is not a Position")
        else:
            return position[0]

    @classmethod
    def get_all_dict(cls) -> dict[str, Position]:
        positions = cls.get_all()

        return {position.singular_name_short: position for position in positions}

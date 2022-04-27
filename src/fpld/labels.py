from __future__ import annotations
from typing import Any, Optional
from .util import API, attrs_sorted
from .constants import API_URL
from functools import cache
from dataclasses import dataclass, field, fields


@dataclass(frozen=True)
class Label:
    label: str
    name: str

    @classmethod
    def from_dict(cls, attr: dict[str, str]) -> Label:
        values = attrs_sorted(cls, attr)

        return cls(*values)

    @classmethod
    @cache
    def get_all(cls) -> list[Label]:
        api = API(API_URL + "/bootstrap-static/")
        labels = api.data["element_stats"]

        labels_ref = [cls.from_dict(label) for label in labels]

        return labels_ref


@dataclass(frozen=True, order=True)
class Position:
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

    @classmethod
    def from_dict(cls, attr: dict[str, str]) -> Label:
        values = attrs_sorted(cls, attr)

        return cls(*values)

    @classmethod
    @cache
    def get_all(cls) -> list[Position]:
        api = API(API_URL + "/bootstrap-static/")
        positions = api.data["element_types"]

        pos_ref = [cls.from_dict(position) for position in positions]

        return pos_ref


def get_label(attr_name: str) -> Optional[Label]:
    labels = Label.get_all()

    for label in labels:
        if label.name == attr_name:
            return label

    return


def get_position(pos_type: int) -> Optional[Position]:
    positions = Position.get_all()

    for position in positions:
        if position.id == pos_type:
            return position

    return

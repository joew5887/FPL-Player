from __future__ import annotations
from dataclasses import dataclass
from typing import TypeVar
from ..util import API
from ..constants import API_URL
from .element import Element


label = TypeVar("label", bound="Label")


@dataclass(frozen=True, kw_only=True)
class Label(Element[label]):
    _DEFAULT_ID = "name"

    label: str
    name: str

    @classmethod
    @property
    def api_link(cls) -> str:
        return API_URL + "/bootstrap-static/"

    @classmethod
    @property
    def get_api(cls) -> dict:
        api = API(cls.api_link)
        return api.data["element_stats"]

    @classmethod
    def get_all_labels(cls) -> list[str]:
        all_labels = cls.get()

        return [label.label for label in all_labels]

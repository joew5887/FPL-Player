from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TypeVar
from ..util import API
from ..constants import URLS
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
        return URLS["BOOTSTRAP-STATIC"]

    @classmethod
    def get_latest_api(cls) -> list[dict[str, Any]]:
        api = super().get_latest_api()
        api = API(cls.api_link)
        data: list
        data = api.data["element_stats"]

        # New labels
        data.append({"label": "Goal Contributions",
                    "name": "goal_contributions"})
        data.append({"label": "Percent Position",
                    "name": "percent_pos"})
        data.append({"label": "Percent Team",
                    "name": "percent_team"})

        return data

    @classmethod
    def get_all_labels(cls) -> list[str]:
        all_labels = cls.get()

        return [label.label for label in all_labels]

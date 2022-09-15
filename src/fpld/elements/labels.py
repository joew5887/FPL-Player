from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TypeVar
from ..util import API
from ..constants import URLS
from .element import Element


@dataclass(frozen=True, order=True, kw_only=True)
class Label(Element["Label"]):
    """Name for FPL player attribute.
    """
    _DEFAULT_ID = "name"
    _ATTR_FOR_STR = "label"

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

        # New player labels
        data.append({"label": "Goal Contributions",
                    "name": "goal_contributions"})
        data.append({"label": "Percent Position",
                    "name": "percent_pos"})
        data.append({"label": "Percent Team",
                    "name": "percent_team"})
        data.append({"label": "Total Points", "name": "total_points"})

        return data

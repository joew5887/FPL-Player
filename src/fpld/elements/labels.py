from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from ..util import API
from ..constants import URLS
from .element import _Element


@dataclass(frozen=True, order=True, kw_only=True)
class Label(_Element["Label"]):
    """Name for FPL player attribute.
    """
    UNIQUE_ID_COL = "name"
    _ATTR_FOR_STR = "label"

    label: str
    name: str

    @classmethod
    @property
    def api_link(cls) -> str:
        return URLS["BOOTSTRAP-STATIC"]

    @classmethod
    def get_latest_api(cls) -> list[dict[str, str]]:
        api = API(cls.api_link)
        data: list[dict[str, str]] = api.data["element_stats"]

        # New player labels
        data.append({"label": "Goal Contributions",
                    "name": "goal_contributions"})
        data.append({"label": "Percent Position",
                    "name": "percent_pos"})
        data.append({"label": "Percent Team",
                    "name": "percent_team"})
        data.append({"label": "Total Points", "name": "total_points"})
        data.append({"label": "Transfers in for next Gameweek", "name": "transfers_in_event"})
        data.append({"label": "Transfers out for next Gameweek", "name": "transfers_out_event"})

        return data

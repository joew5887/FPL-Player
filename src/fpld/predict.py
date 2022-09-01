from __future__ import annotations
from abc import ABC, abstractmethod
from .elements import Player, Team, Event, Fixture
from .elements.element import Element, ElementGroup
import pandas as pd
from typing import TypeVar, Generic
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import numpy as np


elem = TypeVar("elem", bound=Element)


class AttributeModelData(ABC):
    def __init__(self, events_to_use: ElementGroup[Event]):
        self._events = events_to_use

        self.__data = self._set_data()

    @property
    def data(self) -> pd.DataFrame:
        return self.__data

    @property
    def features(self) -> pd.DataFrame:
        return self.data[type(self).feature_columns]

    @property
    def target(self) -> pd.DataFrame:
        return self.data[type(self).target_column]

    def train_test_split_by_random(self, **kwargs) -> tuple:
        return train_test_split(self.features, self.target, **kwargs)

    def train_test_split_by_event(self, testing_events: ElementGroup[Event]) -> tuple:
        event_ids = [event.unique_id for event in testing_events]

        testing = self.__data.query("event in @event_ids")
        training = self.__data.query("event not in @event_ids")

        return training[type(self).feature_columns], testing[type(self).feature_columns], \
            training[type(self).target_column], testing[type(
                self).target_column]

    @abstractmethod
    def _set_data(self) -> pd.DataFrame:
        pass

    @classmethod
    @property
    @abstractmethod
    def feature_columns(cls) -> list[str]:
        return

    @classmethod
    @property
    @abstractmethod
    def target_column(cls) -> str:
        return


class PredictStats(ABC, Generic[elem]):
    def __init__(self, element: elem):
        self.__element = element

    @ property
    def element(self) -> elem:
        return self.__element


class PredictPlayerStats(PredictStats[Player]):
    def __init__(self, player: Player, team_pred: PredictTeamStats):
        super().__init__(player)


# Not used


class PredictTeamStats(PredictStats[Team]):
    def __init__(self, team: Team):
        super().__init__(team)


class GoalsConceded(AttributeModelData):
    def _set_data(self) -> pd.DataFrame:
        data = []

        for event in self._events:
            fixtures_in_event = Fixture.get(event=event.unique_id)
            # last_event_conceded = {team: 1 for team in Team.get_all()}

            fixture: Fixture
            for fixture in fixtures_in_event:
                team_h = fixture.team_h
                team_a = fixture.team_a

                data.append(
                    [
                        event.unique_id,
                        team_h.strength_defence_home,
                        team_a.strength_attack_away,
                        1,
                        team_h.code,
                        fixture.team_h_difficulty,
                        fixture.team_a_score,
                    ]
                )
                data.append(
                    [
                        event.unique_id,
                        team_a.strength_defence_away,
                        team_h.strength_attack_home,
                        0,
                        team_a.code,
                        fixture.team_a_difficulty,
                        fixture.team_h_score,
                    ]
                )

        data_df = pd.DataFrame(
            data, columns=["event"] + type(self).feature_columns + [type(self).target_column])

        return data_df

    @classmethod
    @property
    def feature_columns(cls) -> list[str]:
        return ["defence", "oppo_attack", "was_home", "team", "diff"]

    @classmethod
    @property
    def target_column(cls) -> str:
        return "conceded"

    @ classmethod
    def from_pickle(cls, path: str) -> GoalsConceded:
        return

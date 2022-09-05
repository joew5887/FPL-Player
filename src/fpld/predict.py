from __future__ import annotations
from abc import ABC, abstractmethod
from types import NoneType
from .elements import Player, Team, Event, Fixture
from .elements.element import Element, ElementGroup
import pandas as pd
from typing import Any, TypeVar, Generic, Union
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pickle


elem = TypeVar("elem", bound=Element)
model_type = TypeVar("model_type")
data_type = TypeVar("data_type", bound="AttributeModelData")


class AttributeModelData(ABC):
    def __init__(self, events_to_use: ElementGroup[Event]):
        self._events = events_to_use

        self.__data = self._set_data()

    def __str__(self) -> str:
        return f"""
            {type(self).__name__}
            Events used: {self._events.to_string_list()}
        """

    @property
    def data(self) -> pd.DataFrame:
        return self.__data

    @property
    def features(self) -> pd.DataFrame:
        return self.data[type(self).feature_columns]

    @property
    def target(self) -> pd.DataFrame:
        return self.data[type(self).target_column]

    def save(self, path: str) -> bool:
        with open(path, "wb") as f:
            pickle.dump(self, f)

    def train_test_split_by_random(self, **kwargs) -> tuple:
        x_train, x_test, y_train, y_test = train_test_split(
            self.features, self.target, **kwargs)

        return x_train, x_test, y_train, y_test

    def train_test_split_by_event(self, testing_events: ElementGroup[Event]) -> tuple:
        # range validation needed
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

    @classmethod
    def from_file(cls, path: str) -> AttributeModelData:
        with open(path, "rb") as f:
            return pickle.load(f)


class PointsData(AttributeModelData):
    def _set_data(self) -> pd.DataFrame:
        all_players = Player.get_all()
        data = []

        player: Player
        for player in all_players:
            in_full = player.in_full()
            by_fixture = in_full.history

            for fixture, total_points in zip(by_fixture.fixture, by_fixture.total_points):
                if fixture.event not in self._events:
                    continue

                if fixture.team_h == player.team:
                    data.append(
                        [fixture.event.unique_id, player.code, fixture.team_h_difficulty, 1, total_points])
                else:
                    data.append(
                        [fixture.event.unique_id, player.code, fixture.team_a_difficulty, 0, total_points])

        return pd.DataFrame(data, columns=["event"] + type(self).feature_columns + [type(self).target_column])

    @classmethod
    @property
    def feature_columns(cls) -> list[str]:
        return ["player", "diff", "was_home"]

    @classmethod
    @property
    def target_column(cls) -> str:
        return "total_points"

    @classmethod
    def from_file(cls, path: str) -> PointsData:
        return super().from_file(path)


class __Model(ABC, Generic[data_type, model_type]):
    __x_train: np.ndarray
    __x_test: np.ndarray
    __y_train: np.ndarray
    __y_test: np.ndarray

    def __init__(self, data: data_type, model: model_type):
        self.__model = model
        self.__data = data

        self.__x_train = None
        self.__x_test = None
        self.__y_train = None
        self.__y_test = None

    def __str__(self) -> str:
        return f"""
        {type(self).__name__}
        Model used: {self.model}
        Data used: {self.__data}
        Training method: {self.__training_method}
        """

    @property
    def data(self) -> data_type:
        return self.__data

    @property
    def model(self) -> model_type:
        return self.__model

    def get_final_value(self, player: Player, event: Event) -> float:
        predicted_points = self.get_predicted_points(player, event)
        value = self.get_multiplier_value(player, event)

        return predicted_points * value

    @abstractmethod
    def get_predicted_points(self, player: Player, event: Event) -> int:
        return 0

    @abstractmethod
    def get_multiplier_value(self, player: Player, event: Event) -> float:
        return 0.0

    def save(self, path: str) -> bool:
        self.__data.save(path)

    def fit_by_random(self, **kwargs) -> None:
        x_train, x_test, y_train, y_test = self.__data.train_test_split_by_random(
            **kwargs)
        self.__training_method = "Random"

        self._fit(x_train, x_test, y_train, y_test)

    def fit_by_event(self, testing_events: ElementGroup[Event]) -> None:
        x_train, x_test, y_train, y_test = self.__data.train_test_split_by_event(
            testing_events)
        self.__training_method = "Event"

        self._fit(x_train, x_test, y_train, y_test)

    def fit_by_all(self) -> None:
        x = self.__data.features
        y = self.__data.target
        self.__training_method = "All"

        self._fit(np.array(x), None, np.array(y), None)

    def _fit(self, x_train: np.ndarray, x_test: np.ndarray, y_train: np.ndarray, y_test: np.ndarray) -> None:
        self.model.fit(x_train, y_train)

        self.__x_train = x_train
        self.__x_test = x_test
        self.__y_train = y_train
        self.__y_test = y_test

    def score(self) -> Union[float, NoneType]:
        if self.__x_test is None or self.__y_test is None:
            return None

        return self.model.score(self.__x_test, self.__y_test)

    @classmethod
    def from_file(cls, path: str) -> __Model:
        with open(path, "rb") as f:
            data = pickle.load(f)

        return cls(data)


class PointsModel(__Model[PointsData, RandomForestClassifier]):
    def __init__(self, data: PointsData):
        super().__init__(data, RandomForestClassifier())

    def get_predicted_points(self, player: Player, event: Event) -> int:
        all_team_fixtures = player.team.get_all_fixtures()
        fixtures_in_event = all_team_fixtures.filter(event=event.unique_id)
        code = player.code

        total = 0
        fixture: Fixture
        for fixture in fixtures_in_event:
            diff = fixture.get_difficulty(player.team)

            if fixture.is_home(player.team):
                was_home = 1
            else:
                was_home = 0

            total += sum(self.model.predict([[code, diff, was_home]]))

        return total

    def get_multiplier_value(self, player: Player, event: Event) -> float:
        return 1.0

    @classmethod
    def from_file(cls, path: str) -> PointsModel:
        return super().from_file(path)


class FuturePointsModel():
    def __init__(self, model: __Model, model_gw: Event):
        self.__model = model
        self.__model_gw = model_gw

    @property
    def model(self) -> __Model:
        return self.__model

    def is_updated(self) -> bool:
        return self.__model_gw >= Event.model_gw

    def update(self) -> FuturePointsModel:
        if self.is_updated():
            return self

    @classmethod
    def from_model(cls, model: __Model) -> FuturePointsModel:
        max_gw = max(model.data._events)
        model_gw = max_gw + 1

        if model_gw is None:
            model_gw = max_gw

        return cls(model, model_gw)


# Not used

class PredictStats(ABC, Generic[elem]):
    def __init__(self, element: elem):
        self.__element = element

    @ property
    def element(self) -> elem:
        return self.__element


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

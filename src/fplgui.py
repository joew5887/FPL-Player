import fpld
from typing import Callable, TypeVar, Generic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea, QSpinBox
from fpld.constants import datetime_to_string
from gui.widgets import FilterBox, SearchTable
from gui.widgets.complex import ContentWidget, LineGraph, RefineSearchWidget
from gui.widgets.simple import Label, Table
from gui.widgets.thread import Thread
from gui.windows import Window
from gui.widgets import TitleWidget, AddDefaultHeaders
import pandas as pd
import os


_E = TypeVar("_E", bound=fpld.element.Element)  # need element type restriction


class ElementWidget(ContentWidget, Generic[_E]):
    _element: _E

    def __init__(self, element: _E):
        super().__init__(element=element)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets()

        self._element = kwargs["element"]
        self._tab_widget = QTabWidget()
        self.__info_label = Label.get(self._element.info)
        self.__info_scrollarea = QScrollArea()
        self._layout = QVBoxLayout()

    def setup(self) -> None:
        super().setup()

        self._tab_widget.addTab(self.__info_scrollarea, "Info")

    def add_widgets(self) -> None:
        super().add_widgets()

        self.__info_scrollarea.setWidget(self.__info_label)
        self.__info_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.__info_scrollarea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.__info_scrollarea.setWidgetResizable(True)

        self._layout.addWidget(self._tab_widget)
        self.setLayout(self._layout)

    @classmethod
    def clicked_button(cls, element: _E) -> QPushButton:
        button = QPushButton()

        foo = Window(AddDefaultHeaders(cls(element)), "Element")
        button.clicked.connect(lambda: foo.show())
        button.setText(str(element))

        return button


class PlayerWidget(ElementWidget[fpld.Player]):
    def get_default_header(self) -> TitleWidget:
        title_widget = TitleWidget(
            self._element.web_name, left_txt=str(self._element.team), right_txt=str(self._element.element_type))

        return title_widget

    def get_default_footer(self) -> QWidget:
        return QWidget()


class TeamWidget(ElementWidget[fpld.Team]):
    def get_default_header(self) -> TitleWidget:
        title_widget = TitleWidget(
            self._element.name)

        return title_widget

    def get_default_footer(self) -> QWidget:
        return QWidget()


class HomeWindowTitle(TitleWidget):
    def __init__(self):
        left_txt = self._get_current_gw()
        right_txt = self._get_next_gw()
        super().__init__("SORLOTH", left_txt=left_txt, right_txt=right_txt)

    def _get_current_gw(self) -> None:
        curr_gw = fpld.Event.get_current_gw()

        if curr_gw is not None:
            msg = curr_gw.id
        else:
            msg = "UNKNOWN"

        return f"Current Gameweek: {msg}"

    def _get_next_gw(self) -> None:
        next_gw = fpld.Event.get_next_gw()

        if next_gw is not None:
            msg = next_gw.deadline_time
            msg = datetime_to_string(msg)
        else:
            msg = "UNKNOWN"

        return f"Next gameweek starts: {msg}"


class Home(ContentWidget):
    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)

        self.__layout = QVBoxLayout()
        self.__main_widget = QTabWidget()

    def setup(self) -> None:
        super().setup()

    def add_widgets(self) -> None:
        super().add_widgets()

        self.__main_widget.addTab(self.__get_home(), "Home")
        model = fpld.predict.PointsModel.from_file(
            "C:/Users/joewi/Documents/Python/FPL-Player/lib/points_model")
        model.fit_by_all()
        event = fpld.Event.get_by_id(8)
        points = {player: [model.get_predicted_points(
            player, event)] for player in fpld.Player.get_all()}

        self.__main_widget.addTab(
            AddDefaultHeaders(PointsPredictionTable(model)), "Players")
        self.__main_widget.addTab(
            AddDefaultHeaders(FixtureDifficultyTable()), "Teams")
        self.__main_widget.addTab(
            AddDefaultHeaders(FixtureSearchTable()), "Fixtures")
        self.__main_widget.addTab(
            AddDefaultHeaders(EventSearchTable()), "Events")
        self.__main_widget.addTab(LineGraph(), "Test")
        self.__main_widget.addTab(AddDefaultHeaders(SquadWidget(
            fpld.Squad.optimal_team(points))), "Test2")

        self.__layout.addWidget(self.__main_widget)
        self.setLayout(self.__layout)

    def __get_home(self) -> QScrollArea:
        main_widget = QWidget()
        main_scrollarea = QScrollArea()
        layout = QVBoxLayout()

        layout.addWidget(PlayerSearchTable())
        layout.addWidget(FixtureSearchTable())
        main_widget.setLayout(layout)
        main_scrollarea.setWidget(main_widget)
        main_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        main_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scrollarea.setWidgetResizable(True)

        return main_scrollarea

    def get_default_header(self) -> HomeWindowTitle:
        return HomeWindowTitle()

    def get_default_footer(self) -> QLabel:
        label = QLabel()
        label.setText(
            f"All data from: {fpld.constants.API_URL_STEM}. I do not own any of this data.")

        return label


class FilterBoxes:
    @ classmethod
    def teams(cls) -> FilterBox:
        name = "Team"
        items = fpld.Team.get_all().to_string_list()

        return FilterBox(name, items)

    @ classmethod
    def position(cls) -> FilterBox:
        name = "Position"
        items = fpld.Position.get_all().to_string_list()

        return FilterBox(name, items)

    @ classmethod
    def events(cls, events: fpld.ElementGroup[fpld.Event], all_option: bool = True) -> FilterBox:
        name = "Gameweek"
        current_gw = fpld.Event.get_current_gw()

        items = []
        for event in events:
            if event == current_gw:
                items.append(f"{event} - Current")
            else:
                items.append(str(event))

        return FilterBox(name, items, all_option=all_option)

    @ classmethod
    def __sort(cls, items: list[str]) -> FilterBox:
        name = "Sort By"

        return FilterBox(name, items, all_option=False)

    @ classmethod
    def player_sort(cls) -> FilterBox:
        items = fpld.Label.get_all().to_string_list()

        return cls.__sort(items)

    @ classmethod
    def fixture_sort(cls) -> FilterBox:
        items = ["kickoff_time", "team_h_difficulty", "team_a_difficulty"]

        return cls.__sort(items)

    @ classmethod
    def fixture_difficulty_sort(cls) -> FilterBox:
        items = ["Team", "League Position", "Overall Difficulty"]

        return cls.__sort(items)

    @ classmethod
    def points_prediction_sort(cls) -> FilterBox:
        items = ["Total", "Multiplier", "Model"]

        return cls.__sort(items)


class EventRangeWidget(RefineSearchWidget):
    def __init__(self):
        super().__init__(filter_name="Event Range")

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)

        self.__layout = QVBoxLayout()
        self.__filter_box = QSpinBox()

    def setup(self) -> None:
        super().setup()

        self.__filter_box.setValue(1)
        self.__filter_box.setMinimum(1)
        self.__filter_box.setMaximum(38)

    def add_widgets(self) -> None:
        super().add_widgets()

        self.__layout.addWidget(self._filter_lbl)
        self.__layout.addWidget(self.__filter_box)
        self.setLayout(self.__layout)

    def filter_changed(self, action: Callable) -> None:
        self.__filter_box.valueChanged.connect(action)

    def _access_value(self) -> str:
        return self.__filter_box.value()

    def get_current_option(self) -> int:
        return super().get_current_option()

    def get_event_range(self, event: fpld.Event) -> None:
        event_range = fpld.Event.range(event, 0, self.get_current_option(), 1)
        new_max = 39 - event.unique_id if event.unique_id >= 30 else 10
        self.__filter_box.setMaximum(new_max)

        return event_range


class PlayerSearchTable(SearchTable):
    def __init__(self):
        super().__init__([FilterBoxes.teams(),
                          FilterBoxes.position()], FilterBoxes.player_sort())

    def update_query(self) -> None:
        team = self._filters[0].get_current_option()
        position = self._filters[1].get_current_option()
        sort_by = self._sort.get_current_option()

        query_thread = Thread(lambda: fpld.get_players(
            team=team, position=position, sort_by=sort_by))
        query_thread.signal.return_value.connect(self.update_table)
        self._thread_pool.start(query_thread)

    def update_table(self, df: pd.DataFrame) -> None:
        df["team"] = [TeamWidget.clicked_button(
            team) for team in df["team"]]
        df["player"] = [PlayerWidget.clicked_button(
            player) for player in df["player"]]

        Table.set_data(self._table, df)

    def get_default_header(self) -> QLabel:
        label = Label.get("Players Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()


class FixtureSearchTable(SearchTable):
    def __init__(self):
        super().__init__([FilterBoxes.events(fpld.Event.get_all()),
                          FilterBoxes.teams()], FilterBoxes.fixture_sort())

    def update_query(self) -> None:
        event = self._filters[0].get_current_option()
        team = self._filters[1].get_current_option()
        sort_by = self._sort.get_current_option()

        query_thread = Thread(lambda: fpld.get_fixtures(
            event=event, team=team, sort_by=sort_by))
        query_thread.signal.return_value.connect(self.update_table)
        self._thread_pool.start(query_thread)

    def get_default_header(self) -> QLabel:
        label = Label.get("Fixture Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()


class FixtureDifficultyTable(SearchTable):
    def __init__(self):
        super().__init__([], FilterBoxes.fixture_difficulty_sort())

    def update_query(self) -> None:
        sort_by_name = self._sort.get_current_option()

        all_teams = fpld.Team.get_all()

        if sort_by_name == "League Position":
            all_teams = all_teams.sort("position", reverse=False)
        elif sort_by_name == "Overall Difficulty":
            all_teams = all_teams.sort("fixture_score")

        events = fpld.Event.past_and_future()[1]

        content = []

        team: fpld.Team
        for team in all_teams:
            all_team_fixtures = team.get_all_fixtures()
            row = [str(team)]

            event: fpld.Event
            for event in events:
                fixtures_from_team = fpld.Fixture.get_fixtures_in_event(
                    all_team_fixtures, event.unique_id)
                widget = QWidget()
                widget = FixtureDifficultyTable.get_widget(
                    fixtures_from_team, team)

                row.append(widget)

            content.append(row)

        df = pd.DataFrame(content)
        df.columns = ["Team"] + events.to_string_list()

        self.update_table(df)

    def get_default_header(self) -> QLabel:
        label = Label.get("Fixture Difficulty Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()

    @ staticmethod
    def get_widget(fixtures: fpld.ElementGroup[fpld.Fixture], team: fpld.Team) -> QPushButton:
        DIFF_TO_COLOUR = {1: "#8ace7e", 2: "#309143",
                          3: "#f0bd27", 4: "#ff684c", 5: "#b60a1c"}

        widget = QWidget()
        layout = QHBoxLayout()

        for fixture in fixtures:
            diff = fixture.get_difficulty(team)

            colour = DIFF_TO_COLOUR[diff]

            diff_widget = QPushButton()

            if fixture.is_home(team):
                diff_widget.setText(fixture.team_a.short_name)
            else:
                diff_widget.setText(fixture.team_h.short_name)

            diff_widget.setStyleSheet(f"background-color: {colour}")

            layout.addWidget(diff_widget)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        return widget


class EventSearchTable(SearchTable):
    def __init__(self):
        super().__init__([EventRangeWidget()], None)

    def update_query(self) -> None:
        query_thread = Thread(lambda: fpld.get_events())
        query_thread.signal.return_value.connect(self.update_table)
        self._thread_pool.start(query_thread)

    def get_default_header(self) -> QLabel:
        label = Label.get("Event Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()


class PointsPredictionTable(SearchTable):
    def __init__(self, points_model: fpld.predict.PointsModel):
        self._model = points_model

        super().__init__([FilterBoxes.events(fpld.Event.past_and_future()[1], all_option=False), FilterBoxes.teams(), FilterBoxes.position(), EventRangeWidget()],
                         FilterBoxes.points_prediction_sort())

    def update_query(self) -> None:
        event_range_widget = self._filters[3]
        event_range_widget: EventRangeWidget

        event = self._filters[0].get_current_option()
        event_name = event.split(" - ")[0]
        event_found = fpld.Event.get(name=event_name)[0]

        team = self._filters[1].get_current_option()
        position = self._filters[2].get_current_option()
        event_range = event_range_widget.get_event_range(event_found)
        sort_by = self._sort.get_current_option()

        query_thread = Thread(lambda: self.get_query(
            event, event_range, team, position, sort_by))
        query_thread.signal.return_value.connect(self.update_table)
        self._thread_pool.start(query_thread)

    def get_query(self, event: str, event_range: fpld.ElementGroup[fpld.Event], team: str, position: str, sort_by: str) -> pd.DataFrame:
        df = fpld.get_players(team=team, position=position)
        # Remove default sort column from `get_players()`
        df = df.drop(columns=["total_points"])

        # copied code from fplelems.py get_fixtures()
        event_name = event.split(" - ")[0]
        event_found = fpld.Event.get(name=event_name)[0]

        if sort_by == "Total":
            df["Total"] = df["player"].apply(lambda p: sum(
                self._model.get_final_value(p, e) for e in event_range))
            df = df.sort_values(by=["Total"], ascending=False)
        if sort_by == "Model":
            df["Model"] = df["player"].apply(lambda p: sum(
                self._model.get_predicted_points(p, e) for e in event_range))
            df = df.sort_values(by=["Model"], ascending=False)
        if sort_by == "Multiplier":
            '''df["Multiplier"] = df["player"].apply(lambda p: sum(
                self._model.get_multiplier_value(p, e) for e in event_range))'''
            df["Multiplier"] = [self._model.get_multiplier_value(
                player, event_found) for player in df["player"]]
            df = df.sort_values(by=["Multiplier"], ascending=False)

        return df

    def update_table(self, df: pd.DataFrame) -> None:
        df["team"] = [TeamWidget.clicked_button(
            team) for team in df["team"]]
        df["player"] = [PlayerWidget.clicked_button(
            player) for player in df["player"]]

        Table.set_data(self._table, df)

    def get_default_header(self) -> QLabel:
        label = Label.get("Points Prediction")

        return label

    def get_default_footer(self) -> QWidget:
        label = Label.get()

        return label


class SquadWidget(ContentWidget):
    def __init__(self, squad: fpld.Squad):
        self.squad = squad
        super().__init__()

    @ property
    def squad(self) -> fpld.Squad:
        return self.__squad

    @ squad.setter
    def squad(self, new_squad: fpld.Squad) -> None:
        self.__squad = new_squad

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets()

        self.__layout = QVBoxLayout()
        self.__gk_layout = QHBoxLayout()
        self.__def_layout = QHBoxLayout()
        self.__mid_layout = QHBoxLayout()
        self.__fwd_layout = QHBoxLayout()

        positions = fpld.Position.get_all()
        self.__full_team_layouts = {
            position: layout for position, layout in zip(positions, [self.__gk_layout, self.__def_layout, self.__mid_layout, self.__fwd_layout])}
        self.__bench_layout = QHBoxLayout()

    def setup(self) -> None:
        self.__add_players()
        self.__layout.setSpacing(0)
        super().setup()

    def add_widgets(self) -> None:
        super().add_widgets()

        gk_widget = QWidget()
        def_widget = QWidget()
        mid_widget = QWidget()
        fwd_widget = QWidget()

        LIGHT_GREEN = "rgb(96, 168, 48)"
        DARK_GREEN = "rgb(9, 148, 65)"
        gk_widget.setStyleSheet(f"background-color:{DARK_GREEN};")
        mid_widget.setStyleSheet(f"background-color:{DARK_GREEN};")
        def_widget.setStyleSheet(f"background-color:{LIGHT_GREEN};")
        fwd_widget.setStyleSheet(f"background-color:{LIGHT_GREEN};")

        bench_widget = QWidget()

        gk_widget.setLayout(self.__gk_layout)
        def_widget.setLayout(self.__def_layout)
        mid_widget.setLayout(self.__mid_layout)
        fwd_widget.setLayout(self.__fwd_layout)
        bench_widget.setLayout(self.__bench_layout)

        self.__layout.addWidget(gk_widget)
        self.__layout.addWidget(def_widget)
        self.__layout.addWidget(mid_widget)
        self.__layout.addWidget(fwd_widget)
        self.__layout.addWidget(bench_widget)

        self.setLayout(self.__layout)

    def get_default_header(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()
        cost_lbl = Label.get(f"Cost: {self.squad.cost}")

        layout.addWidget(cost_lbl)
        widget.setLayout(layout)

        return widget

    def get_default_footer(self) -> QWidget:
        return QWidget()

    def __add_players(self) -> None:
        for player in self.squad.starting_team:
            widget = PlayerWidget.clicked_button(player)

            if player == self.squad.captain:
                widget.setText(widget.text() + " (C)")

            if player == self.squad.vice_captain:
                widget.setText(widget.text() + " (VC)")

            self.__full_team_layouts[player.element_type].addWidget(widget)

        for player in self.squad.bench:
            widget = PlayerWidget.clicked_button(player)

            self.__bench_layout.addWidget(widget)

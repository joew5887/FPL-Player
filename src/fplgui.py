import fpld
from typing import TypeVar, Generic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea
from fpld.elements.element import ElementGroup
from fpld.constants import datetime_to_string
from gui.widgets import FilterBox, SearchTable
from gui.widgets.complex import ContentWidget, LineGraph
from gui.widgets.simple import Label, Table
from gui.windows import Window
from gui.widgets import TitleWidget, AddHeaders
import pandas as pd


_E = TypeVar("_E")  # need element type restriction


class ElementWidget(ContentWidget, Generic[_E]):
    _element: _E

    def __init__(self, element: _E):
        super().__init__(element=element)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets()

        self._element = kwargs["element"]
        self._layout = QVBoxLayout()

    def setup(self) -> None:
        super().setup()

    def add_widgets(self) -> None:
        super().add_widgets()

        self.setLayout(self._layout)

    @classmethod
    def clicked_button(cls, element: _E) -> QPushButton:
        button = QPushButton()

        foo = Window(cls.add_default_headers(element))
        button.clicked.connect(lambda: foo.show())
        button.setText(str(element))

        return button

    @classmethod
    def add_default_headers(cls, element: _E) -> AddHeaders:
        main = cls(element)

        header = main.get_default_header()
        footer = main.get_default_footer()

        return AddHeaders(main, header=header, footer=footer)


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
        curr_gw = fpld.Event.current_gw
        if curr_gw is not None:
            msg = curr_gw.id
        else:
            msg = "UNKNOWN"

        return f"Current Gameweek: {msg}"

    def _get_next_gw(self) -> None:
        next_gw = fpld.Event.next_gw
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
        self.__main_widget.addTab(
            PlayerSearchTable.add_default_headers(), "Players")
        self.__main_widget.addTab(
            FixtureDifficultyTable.add_default_headers(), "Teams")
        self.__main_widget.addTab(
            FixtureSearchTable.add_default_headers(), "Fixtures")
        self.__main_widget.addTab(
            EventSearchTable.add_default_headers(), "Events")
        self.__main_widget.addTab(LineGraph(), "Test")

        self.__layout.addWidget(self.__main_widget)
        self.setLayout(self.__layout)

    def __get_home(self) -> QScrollArea:
        main_widget = QWidget()
        main_scrollarea = QScrollArea()
        layout = QVBoxLayout()

        layout.addWidget(PlayerSearchTable.add_default_headers())
        layout.addWidget(FixtureSearchTable.add_default_headers())
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
    def events(cls) -> FilterBox:
        name = "Gameweek"
        events = fpld.Event.get_all()
        current_gw = fpld.Event.current_gw

        items = []
        for event in events:
            if event == current_gw:
                items.append(f"{event} - Current")
            else:
                items.append(str(event))

        return FilterBox(name, items)

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


class PlayerSearchTable(SearchTable):
    __teams: ElementGroup[fpld.Team]
    __positions: ElementGroup[fpld.Position]
    __players: ElementGroup[fpld.Player]

    def __init__(self):
        super().__init__([FilterBoxes.teams(),
                          FilterBoxes.position()], FilterBoxes.player_sort())

    def get_query(self) -> None:
        team = self._filters[0].get_current_option()
        position = self._filters[1].get_current_option()

        if team == "All":
            self.__teams = fpld.Team.get()
        else:
            self.__teams = fpld.Team.get(name=team)

        if position == "All":
            self.__positions = fpld.Position.get()
        else:
            self.__positions = fpld.Position.get(singular_name=position)

        self.__players = fpld.Player.get(element_type=tuple(
            self.__positions), team=tuple(self.__teams))

        sort_by_name = self._sort.get_current_option()
        label = fpld.Label.get(label=sort_by_name)[0]
        self.__players = self.__players.sort(label.name)

        df = self.__create_df(label)
        Table.set_data(self._table, df)

    def __create_df(self, label: fpld.Label) -> pd.DataFrame:
        df = self.__players.to_df("element_type", label.name)
        df["team"] = [TeamWidget.clicked_button(
            player.team) for player in self.__players]
        df["player"] = [PlayerWidget.clicked_button(
            player) for player in self.__players]
        df = df[["player", "team", "element_type", label.name]]

        return df

    def get_default_header(self) -> QLabel:
        label = Label.get("Players Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()


class FixtureSearchTable(SearchTable):
    __events: ElementGroup[fpld.Event]
    __fixtures: ElementGroup[fpld.Fixture]

    def __init__(self):
        super().__init__([FilterBoxes.events(),
                          FilterBoxes.teams()], FilterBoxes.fixture_sort())

    def get_query(self) -> None:
        self.__events = fpld.Event.get_all()

        event = self._filters[0].get_current_option()
        team = self._filters[1].get_current_option()

        if event == "All":
            self.__events = fpld.Event.get()
        else:
            event_name = event.split(" - ")[0]
            self.__events = fpld.Event.get(name=event_name)

        self.__fixtures = fpld.Fixture.get(event=tuple(self.__events))

        if team != "All":
            team_obj = fpld.Team.get(name=team)[0]
            self.__fixtures = self.__fixtures.filter(
                method_="or", team_h=team_obj, team_a=team_obj)

        sort_by_name = self._sort.get_current_option()

        if sort_by_name == "kickoff_time":
            reverse_ = False
        else:
            reverse_ = True
        # label = fpld.Label.get(label=sort_by_name)[0]
        self.__fixtures = self.__fixtures.sort(sort_by_name, reverse=reverse_)

        df = self.__fixtures.to_df("score", "event", sort_by_name)

        if sort_by_name == "kickoff_time":
            df["kickoff_time"] = df["kickoff_time"].apply(
                lambda date_: datetime_to_string(date_))

        Table.set_data(self._table, df)

    def get_default_header(self) -> QLabel:
        label = Label.get("Fixture Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()


class FixtureDifficultyTable(SearchTable):
    def __init__(self):
        super().__init__([], FilterBoxes.fixture_difficulty_sort())

    def get_query(self) -> None:
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
        Table.set_data(self._table, df)

    def get_default_header(self) -> QLabel:
        label = Label.get("Fixture Difficulty Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()

    @ staticmethod
    def get_widget(fixtures: ElementGroup[fpld.Fixture], team: fpld.Team) -> QPushButton:
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
        super().__init__([], FilterBoxes.fixture_difficulty_sort())

    def get_query(self) -> None:
        df = fpld.Event.get_all().to_df("name", "deadline_time",
                                        "most_selected", "most_transferred_in", "most_captained",
                                        "most_vice_captained", "finished")
        df["deadline_time"] = df["deadline_time"].apply(
            lambda date_: datetime_to_string(date_))
        Table.set_data(self._table, df)

    def get_default_header(self) -> QLabel:
        label = Label.get("Event Search")

        return label

    def get_default_footer(self) -> QWidget:
        return QWidget()

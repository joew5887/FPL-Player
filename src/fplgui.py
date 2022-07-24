import fpld
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea
from fpld.elements.element import ElementGroup
from gui.widgets import FilterBox, SearchTable, TableWithTitle
from gui.widgets.complex import ComplexWidget
from gui.widgets.simple import Label, Table
from gui.windows import DefaultWindow
from gui.widgets import TitleWidget
import pandas as pd


class HomeWindow(DefaultWindow):
    def __init__(self):
        main_widget = self.__get_home()
        super().__init__(HomeWindowTitle(), main_widget)

    def __get_home(self) -> QWidget:
        x = QTabWidget()
        test = QWidget()

        z = QScrollArea()
        layout = QVBoxLayout()
        layout.addWidget(PlayerSearchTable())
        layout.addWidget(FixtureSearchTable())
        test.setLayout(layout)
        z.setWidget(test)
        z.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        z.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        z.setWidgetResizable(True)
        x.addTab(z, "Home")

        for i in ["Events"]:
            z = TableWithTitle(i)
            x.addTab(z, i)

        x.addTab(PlayerSearchTable(), "Players")
        x.addTab(FixtureSearchTable(), "Fixtures")
        x.addTab(FixtureDifficultyTable(), "Teams")

        return x


class ElementWindow(DefaultWindow):
    pass


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
        else:
            msg = "UNKNOWN"

        return f"Next gameweek starts: {msg}"


class FilterBoxes:
    @classmethod
    def teams(cls) -> FilterBox:
        name = "Team"
        items = fpld.Team.get_all().string_list()

        return FilterBox(name, items)

    @classmethod
    def position(cls) -> FilterBox:
        name = "Position"
        items = fpld.Position.get_all().string_list()

        return FilterBox(name, items)

    @classmethod
    def events(cls) -> FilterBox:
        name = "Gameweek"
        items = fpld.Event.get_all().string_list()

        return FilterBox(name, items)

    @classmethod
    def __sort(cls, items: list[str]) -> FilterBox:
        name = "Sort By"

        return FilterBox(name, items, all_option=False)

    @classmethod
    def player_sort(cls) -> FilterBox:
        items = fpld.Label.get_all().string_list()

        return cls.__sort(items)

    @classmethod
    def fixture_sort(cls) -> FilterBox:
        items = ["kickoff_time", "team_h_difficulty", "team_a_difficulty"]

        return cls.__sort(items)

    @classmethod
    def fixture_difficulty_sort(cls) -> FilterBox:
        items = ["Team", "League Position", "Overall Difficulty"]

        return cls.__sort(items)


class PlayerSearchTable(SearchTable):
    __teams: ElementGroup[fpld.Team]
    __positions: ElementGroup[fpld.Position]
    __players: ElementGroup[fpld.Player]

    def __init__(self):
        super().__init__("Player Search", [FilterBoxes.teams(),
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

        df = self.__players.as_df(
            "web_name", "team", "element_type", label.name)
        Table.set_data(self._table, df)


class FixtureSearchTable(SearchTable):
    __events: ElementGroup[fpld.Event]
    __fixtures: ElementGroup[fpld.Fixture]

    def __init__(self):
        super().__init__("Fixture Search", [FilterBoxes.events(),
                                            FilterBoxes.teams()], FilterBoxes.fixture_sort())

    def get_query(self) -> None:
        self.__events = fpld.Event.get_all()

        event = self._filters[0].get_current_option()
        team = self._filters[1].get_current_option()

        if event == "All":
            self.__events = fpld.Event.get()
        else:
            self.__events = fpld.Event.get(name=event)

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

        df = self.__fixtures.as_df("fixture", "event", sort_by_name)
        Table.set_data(self._table, df)


class FixtureDifficultyTable(SearchTable):
    def __init__(self):
        super().__init__("Fixture Difficulty", [], FilterBoxes.fixture_difficulty_sort())

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
            row = [str(team)]

            for event in events:
                fixtures_from_team = team.fixtures_from_event(event)
                widget = QWidget()
                widget = FixtureDifficultyTable.get_widget(
                    fixtures_from_team, team)

                row.append(widget)

            content.append(row)

        df = pd.DataFrame(content)
        df.columns = ["Team"] + events.string_list()
        Table.set_data(self._table, df)

    @ staticmethod
    def get_widget(fixtures: ElementGroup[fpld.Fixture], team: fpld.Team) -> QPushButton:
        DIFF_TO_COLOUR = {1: "#8ace7e", 2: "#309143",
                          3: "#f0bd27", 4: "#ff684c", 5: "#b60a1c"}

        widget = QWidget()
        layout = QHBoxLayout()

        for fixture in fixtures:
            if fixture.team_h == team:
                diff = fixture.team_h_difficulty
            elif fixture.team_a == team:
                diff = fixture.team_a_difficulty
            else:
                raise ValueError("Team not in fixture")

            colour = DIFF_TO_COLOUR[diff]

            diff_widget = QPushButton()
            diff_widget.setText(str(diff))
            diff_widget.setStyleSheet(f"background-color: {colour}")

            layout.addWidget(diff_widget)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        return widget

    @ staticmethod
    def get_widget2(difficulty: int) -> QPushButton:
        DIFF_TO_COLOUR = {1: "#8ace7e", 2: "#309143",
                          3: "#f0bd27", 4: "#ff684c", 5: "#b60a1c"}
        colour = DIFF_TO_COLOUR[difficulty]

        widget = QPushButton()
        widget.setText(str(difficulty))
        widget.setStyleSheet(f"background-color: {colour}")

        return widget

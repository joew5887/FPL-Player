from logging import Filter
import fpld
from PyQt5.QtWidgets import QTabWidget, QWidget
from fpld.elements.element import ElementGroup
from gui.widgets import FilterBox, SearchTable
from gui.widgets.simple import Table
from gui.windows import DefaultWindow
from gui.widgets import TitleWidget


class HomeWindow(DefaultWindow):
    def __init__(self):
        main_widget = self.__get_home()
        super().__init__(HomeWindowTitle(), main_widget)

    def __get_home(self) -> QWidget:
        x = QTabWidget()
        y = FixtureSearchTable()
        x.addTab(y, "Home")

        for i in ["Players", "Teams", "Fixtures", "Events"]:
            z = FilterBox(i, ["1", "2", "3"])
            # z = FilterBox(i, [])
            x.addTab(z, i)

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
        items = fpld.Team.get().string_list()

        return FilterBox(name, items)

    @classmethod
    def position(cls) -> FilterBox:
        name = "Position"
        items = fpld.Position.get().string_list()

        return FilterBox(name, items)

    @classmethod
    def events(cls) -> FilterBox:
        name = "Gameweek"
        items = fpld.Event.get().string_list()

        return FilterBox(name, items)

    @classmethod
    def player_sort(cls) -> FilterBox:
        name = "Sort By"
        items = fpld.Label.get().string_list()

        return FilterBox(name, items, all_option=False)

    @classmethod
    def fixture_sort(cls) -> FilterBox:
        name = "Sort By"
        items = ["kickoff_time", "team_h_difficulty", "team_a_difficulty"]

        return FilterBox(name, items, all_option=False)


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

        df = self.__players.as_df(
            "web_name", "team", "element_type", label.name)
        Table.set_data(self._table, df)


class FixtureSearchTable(SearchTable):
    __events: ElementGroup[fpld.Event]
    __fixtures: ElementGroup[fpld.Fixture]

    def __init__(self):
        super().__init__([FilterBoxes.events()], FilterBoxes.fixture_sort())

    def get_query(self) -> None:
        event = self._filters[0].get_current_option()

        if event == "All":
            self.__events = fpld.Event.get()
        else:
            self.__events = fpld.Event.get(name=event)

        self.__fixtures = fpld.Fixture.get(event=tuple(self.__events))

        sort_by_name = self._sort.get_current_option()

        if sort_by_name == "kickoff_time":
            reverse_ = False
        else:
            reverse_ = True
        # label = fpld.Label.get(label=sort_by_name)[0]
        self.__fixtures = self.__fixtures.sort(sort_by_name, reverse=reverse_)

        df = self.__fixtures.as_df("desc", "event", sort_by_name)
        Table.set_data(self._table, df)

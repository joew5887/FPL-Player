from .parent import FPLWindow, set_dropbox
from PyQt5.QtWidgets import (
    QGridLayout, QComboBox, QLabel, QLineEdit, QTableWidget, QHBoxLayout, QVBoxLayout, QTreeWidget)
import fpld
from .thread import LongTask


class SearchScrn(FPLWindow):
    filter_layout: QGridLayout
    position_box: QComboBox
    position_lbl: QLabel
    team_box: QComboBox
    team_lbl: QLabel
    output_sort_layout: QHBoxLayout
    sort_layout: QVBoxLayout
    columns_tree: QTreeWidget
    order_by_tree: QTreeWidget
    input_txt: QLineEdit
    output_tbl: QTableWidget
    title_lbl: QLabel
    __current_teams: list[fpld.Team]
    __current_positions: list[fpld.Position]
    __players: list[fpld.Player]

    def __init__(self):
        super().__init__("search.ui")
        self.team_box.currentIndexChanged.connect(
            lambda: self.__team_search(self.team_box.currentText())
        )
        self.position_box.currentIndexChanged.connect(
            lambda: self.__position_search(self.position_box.currentText())
        )
        self.__current_teams = []
        self.__current_positions = []
        self.__players = []

    def _set_widgets(self) -> None:  # Add thread support
        self.position_lbl.setText("Position")
        self.team_lbl.setText("Team")

        tasks = {
            "Getting all teams": self.__set_team_box,
            "Getting all player positions": self.__set_position_box
        }
        x = LongTask(tasks, self.show)
        x.start()

    def __set_team_box(self) -> None:
        all_names = fpld.Team.get_all_names()
        set_dropbox(self.team_box, all_names)

    def __set_position_box(self) -> None:
        all_names = fpld.Position.get_all_names()
        set_dropbox(self.position_box, all_names)

    def __team_search(self, team_name: str) -> None:
        task = {
            "Updating team search": lambda: self.__update_current_teams(team_name)}
        x = LongTask(task, self.__edit_search)
        x.start()

    def __update_current_teams(self, team_name: str) -> None:
        if team_name == "All":
            self.__current_teams = fpld.Team.get()
        else:
            self.__current_teams = fpld.Team.get(name=team_name)

    def __position_search(self, position_name: str) -> None:
        task = {"Updating position search": lambda: self.__update_current_positions(
            position_name)}
        x = LongTask(task, self.__edit_search)
        x.start()

    def __update_current_positions(self, position_name: str) -> None:
        if position_name == "All":
            self.__current_positions = fpld.Position.get()
        else:
            self.__current_positions = fpld.Position.get(
                singular_name=position_name)

    def __edit_search(self) -> None:
        self.__players = []

        for team in self.__current_teams:
            for player in team.players:
                if player.element_type in self.__current_positions:
                    self.__players.append(player)

        self.__display_search()

    def __display_search(self) -> None:
        print("")
        for p in self.__players:
            print(p)

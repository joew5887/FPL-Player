from .parent import FPLWindow, Filter, set_dropbox, label_wrapper, combo_box_wrapper, set_table
from PyQt5.QtWidgets import (
    QGridLayout, QComboBox, QLabel, QTableWidget, QHBoxLayout, )
import fpld
from .thread import LongTask
import pandas as pd


class SearchScrn(FPLWindow):
    filter_layout: QGridLayout
    position_box: QComboBox
    position_lbl: QLabel
    team_box: QComboBox
    team_lbl: QLabel
    order_by_layout: QHBoxLayout
    order_by_box: QComboBox
    order_by_lbl: QLabel
    output_tbl: QTableWidget
    title_lbl: QLabel
    __teams: list[fpld.Team]
    __positions: list[fpld.Position]
    __players: list[fpld.Player]
    __order_by: fpld.Label
    __position_filter: Filter
    __team_filter: Filter
    __order_by_filter: Filter

    def __init__(self):
        super().__init__("search.ui")

    def __bar(self):
        self.team_box.currentIndexChanged.connect(
            self.__edit_filters
        )
        self.position_box.currentIndexChanged.connect(
            self.__edit_filters
        )
        self.order_by_box.currentIndexChanged.connect(
            self.__edit_filters
        )
        self.__edit_filters()
        self.show()

    def _set_widgets(self) -> None:
        self.__position_filter = Filter(
            self.position_lbl, self.position_box, "Position", fpld.Position.get_all_names)
        self.__team_filter = Filter(self.team_lbl, self.team_box,
                                    "Team", fpld.Team.get_all_names)
        self.__order_by_filter = Filter(self.order_by_lbl, self.order_by_box,
                                        "Order by", fpld.Label.get_all_labels, all_option=False)

        tasks = {
            "Getting all teams": self.__team_filter.setup,
            "Getting all player positions": self.__position_filter.setup,
            "Getting attributes": self.__order_by_filter.setup,
        }
        setup_thread = LongTask(tasks, self.__bar)
        setup_thread.start()

    def __update_current_teams(self) -> None:
        self.__teams = fpld.Team.gui_get(
            self.__team_filter.current_option)

    def __update_current_positions(self) -> None:
        self.__positions = fpld.Position.gui_get(
            self.__position_filter.current_option)

    def __update_order_by(self) -> None:
        self.__order_by = fpld.Label.get(
            label=self.__order_by_filter.current_option)[0]

    def __edit_filters(self) -> None:
        tasks = {
            "Updating team search": self.__update_current_teams,
            "Updating position search": self.__update_current_positions,
            "Updating sort function": self.__update_order_by
        }
        x = LongTask(tasks, self.__update_search)
        x.start()

    def __update_search(self) -> None:
        self.__players = fpld.Player.get(team=tuple(
            self.__teams), element_type=tuple(self.__positions))
        self.__players = fpld.Player.sort(
            self.__players, self.__order_by.name)
        self.__display_search()

    def __display_search(self) -> None:
        set_table(self.output_tbl, pd.DataFrame(
            [[p, getattr(p, self.__order_by.name)] for p in self.__players]))

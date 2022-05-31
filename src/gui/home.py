from .parent import FPLWindow, set_text_label
from .search import SearchScrn
from PyQt5.QtWidgets import (QGridLayout, QPushButton, QLabel)
from fpld import Event
from .thread import LongTask


class HomeScrn(FPLWindow):
    menu_layout: QGridLayout
    search_btn: QPushButton
    stats_btn: QPushButton
    team_btn: QPushButton
    info_layout: QGridLayout
    info1_lbl: QLabel
    info2_lbl: QLabel
    title_lbl: QLabel

    def __init__(self):
        super().__init__("home.ui")

    def _set_widgets(self) -> None:
        self.search_btn.clicked.connect(self.open_search)

        tasks = {
            "Getting current gameweek": self.__set_info1_lbl,
            "Getting next gameweek": self.__set_info2_lbl
        }
        x = LongTask(tasks, self.show)
        x.start()

        self.title_lbl.setText("Home")

    def __set_info1_lbl(self) -> None:
        curr_gw = Event.current_gw
        if curr_gw is not None:
            msg = curr_gw.id
        else:
            msg = "UNKNOWN"

        set_text_label(
            self.info1_lbl, f"Current Gameweek: {msg}")

    def __set_info2_lbl(self) -> None:
        next_gw = Event.next_gw
        if next_gw is not None:
            msg = next_gw.deadline_time
        else:
            msg = "UNKNOWN"

        set_text_label(
            self.info2_lbl, f"Next gameweek starts: {msg}")

    def open_search(self) -> None:
        page = SearchScrn()

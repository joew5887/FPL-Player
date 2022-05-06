from .parent import FPLWindow, set_text_label
from .search import SearchScrn
from PyQt5.QtWidgets import (QGridLayout, QPushButton, QLabel)
from fpld import Event


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

        set_text_label(
            self.info1_lbl, f"Current Gameweek: {Event.current_gw.id}")
        set_text_label(
            self.info2_lbl, f"Next gameweek starts: {Event.next_gw.deadline_time}")

        self.title_lbl.setText("Home")

    def open_search(self) -> None:
        page = SearchScrn()
        page.show()

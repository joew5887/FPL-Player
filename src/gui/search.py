from .parent import FPLWindow, set_dropbox
from PyQt5.QtWidgets import (
    QGridLayout, QComboBox, QLabel, QLineEdit, QTableWidget)
import fpld
from .thread import LongTask


class SearchScrn(FPLWindow):
    filter_layout: QGridLayout
    position_box: QComboBox
    position_lbl: QLabel
    team_box: QComboBox
    team_lbl: QLabel
    input_txt: QLineEdit
    output_tbl: QTableWidget
    title_lbl: QLabel

    def __init__(self):
        super().__init__("search.ui")

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
        all_teams = fpld.Team.get()
        all_names = [team.name for team in all_teams]
        set_dropbox(self.team_box, all_names)

    def __set_position_box(self) -> None:
        all_positions = fpld.Position.get()
        all_names = [position.singular_name for position in all_positions]
        set_dropbox(self.position_box, all_names)

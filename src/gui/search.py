from .parent import FPLWindow
from PyQt5.QtWidgets import (
    QGridLayout, QComboBox, QLabel, QLineEdit, QTableWidget)
import fpld


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

        # Team filter
        self.team_lbl.setText("Team")
        self.__set_team_box()
        self.__set_position_box()

    def __set_team_box(self) -> None:
        all_teams = fpld.Team.get()

        team: fpld.Team
        for team in all_teams:
            self.team_box.addItem(team.name)

        self.team_box.addItem("All")

    def __set_position_box(self) -> None:
        all_positions = fpld.Position.get()

        position: fpld.Position
        for position in all_positions:
            self.position_box.addItem(position.singular_name)

        self.position_box.addItem("All")

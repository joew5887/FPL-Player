from PyQt5.QtWidgets import (
    QLabel, QWidget,
    QHBoxLayout
)
from PyQt5.QtCore import Qt
from abc import abstractmethod
from .simple import Title, Label
from typing import Callable
import fpld


class ComplexWidget(QWidget):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def display(self) -> None:
        pass


class TitleWidget(ComplexWidget):
    def __init__(self):
        super().__init__()
        self.__layout = QHBoxLayout()
        self._title_lbl = Title.get()
        self._info1_lbl = Label.get()
        self._info2_lbl = Label.get()

    def _set_labels(self) -> None:
        self._set_title_lbl()
        self._set_left_lbl()
        self._set_right_lbl()

    def setup(self) -> None:
        self._info2_lbl.setAlignment(Qt.AlignRight)
        self._info1_lbl.setAlignment(Qt.AlignLeft)
        self._title_lbl.setAlignment(Qt.AlignHCenter)

        self._set_labels()

    def display(self) -> None:
        self.__layout.addWidget(self._info1_lbl)
        self.__layout.addWidget(self._title_lbl)
        self.__layout.addWidget(self._info2_lbl)
        self.setLayout(self.__layout)

    @abstractmethod
    def _set_title_lbl(self) -> None:
        self._title_lbl.setText("Title")

    @abstractmethod
    def _set_left_lbl(self) -> None:
        self._info1_lbl.setText("L")

    @abstractmethod
    def _set_right_lbl(self) -> None:
        self._info2_lbl.setText("R")


class HomeWindowTitle(TitleWidget):
    def _set_title_lbl(self) -> None:
        self._title_lbl.setText("SORLOTH")

    def _set_left_lbl(self) -> None:
        curr_gw = fpld.Event.current_gw
        if curr_gw is not None:
            msg = curr_gw.id
        else:
            msg = "UNKNOWN"

        self._info1_lbl.setText(f"Current Gameweek: {msg}")

    def _set_right_lbl(self) -> None:
        next_gw = fpld.Event.next_gw
        if next_gw is not None:
            msg = next_gw.deadline_time
        else:
            msg = "UNKNOWN"

        self._info2_lbl.setText(f"Next gameweek starts: {msg}")

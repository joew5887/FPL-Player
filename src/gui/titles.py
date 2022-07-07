from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from abc import abstractmethod
from typing import Callable
from .thread import LongTask
from .format_widgets import title_label_wrapper, label_wrapper
import fpld


class Title(QWidget):
    def __init__(self):
        super().__init__()
        self.__layout = QHBoxLayout()
        self._title_lbl = QLabel()
        self._info1_lbl = QLabel()
        self._info2_lbl = QLabel()

        self._set_widgets()

    @abstractmethod
    def action_to_labels(self) -> dict[str, Callable]:
        return {
            "Label 1": lambda: self.__set_lbl1(self._info1_lbl),
            "Label 2": lambda: self.__set_lbl2(self._info2_lbl)
        }

    def _set_widgets(self) -> None:
        self._set_title_lbl()
        self._info2_lbl.setAlignment(Qt.AlignRight)
        self._info1_lbl.setAlignment(Qt.AlignLeft)
        self._title_lbl.setAlignment(Qt.AlignHCenter)

        tasks = self.action_to_labels()
        x = LongTask(tasks, self.__layer_widgets)
        x.start()

    def __layer_widgets(self) -> None:
        self.__layout.addWidget(self._info1_lbl)
        self.__layout.addWidget(self._title_lbl)
        self.__layout.addWidget(self._info2_lbl)
        self.setLayout(self.__layout)

    @abstractmethod
    def _set_title_lbl(self) -> None:
        return

    def __set_lbl1(self, label: QLabel) -> None:
        return

    def __set_lbl2(self, label: QLabel) -> None:
        return


class FPLWindowTitle(Title):
    def action_to_labels(self) -> dict[str, Callable]:
        return {
            "Getting current gameweek": lambda: self._current_gw_lbl(self._info1_lbl),
            "Getting next gameweek": lambda: self._next_gw_lbl(self._info2_lbl)
        }

    def _set_title_lbl(self) -> None:
        title_label_wrapper(self._title_lbl, "SORLOTH")

    def _current_gw_lbl(self, label: QLabel) -> None:
        curr_gw = fpld.Event.current_gw
        if curr_gw is not None:
            msg = curr_gw.id
        else:
            msg = "UNKNOWN"

        label_wrapper(
            label, f"Current Gameweek: {msg}")

    def _next_gw_lbl(self, label: QLabel) -> None:
        next_gw = fpld.Event.next_gw
        if next_gw is not None:
            msg = next_gw.deadline_time
        else:
            msg = "UNKNOWN"

        label_wrapper(
            label, f"Next gameweek starts: {msg}")

from abc import abstractmethod, ABC
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont


GUI_STEM = ".//lib//"


class FPLWindow(QMainWindow):
    title_lbl: QLabel
    screen_layout: QVBoxLayout

    def __init__(self, window_name: str):
        super().__init__()
        self.__ui = loadUi(GUI_STEM + window_name, self)
        self._set_widgets()

    @abstractmethod
    def _set_widgets(self) -> None:
        pass

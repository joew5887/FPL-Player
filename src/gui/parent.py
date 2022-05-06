from __future__ import annotations
from abc import abstractmethod
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QComboBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont


GUI_STEM = ".//lib//"


class FPLWindow(QMainWindow):
    title_lbl: QLabel
    screen_layout: QVBoxLayout

    def __init__(self, window_name: str):
        super().__init__()
        self.__ui = loadUi(GUI_STEM + window_name, self)
        self.__set_common_widgets()
        self._set_widgets()

    @abstractmethod
    def _set_widgets(self) -> None:
        pass

    def __set_common_widgets(self) -> None:
        _title_label_wrapper(self.title_lbl)


def label_wrapper(label: QLabel, font: QFont) -> None:
    label.setFont(font)


def _title_label_wrapper(label: QLabel) -> None:
    SIZE = 18
    FONT_TYPE = "Arial Rounded MT Bold"

    font = QFont(FONT_TYPE, SIZE)
    font.setBold(True)
    label_wrapper(label, font)


def _text_label_wrapper(label: QLabel) -> None:
    SIZE = 14
    FONT_TYPE = "Arial"

    font = QFont(FONT_TYPE, SIZE)
    label_wrapper(label, font)


def set_text_label(label: QLabel, text: str) -> None:
    label.setText(text)
    _text_label_wrapper(label)


def set_dropbox(box: QComboBox, items: list[str], *, all_option: bool = True) -> None:
    if all_option:
        items.insert(0, "All")

    box.addItems(items)

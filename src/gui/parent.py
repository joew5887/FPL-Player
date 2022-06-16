from __future__ import annotations
from abc import abstractmethod
from typing import Callable
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QComboBox, QMessageBox, QWidget,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont
import pandas as pd


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
        title_label_wrapper(self.title_lbl)
        self._resize()

    def _resize(self) -> None:
        self.resize(1200, 800)
        widget = QWidget()
        widget.setLayout(self.screen_layout)
        self.setCentralWidget(widget)


class Filter:
    def __init__(self, label: QLabel, box: QComboBox,
                 label_str: str, box_list: Callable[..., list[str]],
                 *, all_option: bool = True):

        self.__label = label
        self.__box = box
        self.__box_list = box_list
        self.__all_option = all_option
        label_wrapper(self.__label, label_str)
        combo_box_wrapper(self.__box)

    @property
    def current_option(self) -> str:
        return self.__box.currentText()

    def setup(self) -> None:
        items = self.__box_list()
        set_dropbox(self.__box, items, all_option=self.__all_option)


class Widget:
    def __init__(self, widget: QWidget, font: QFont):
        self._widget = widget
        self._widget.setFont(font)


class Label(Widget):
    _widget: QLabel

    def __init__(self, label: QLabel, font: QFont, text: str = None):
        super().__init__(label, font)
        label.setText(text)


class TitleLabel(Label):
    def __init__(self, label: QLabel, font: QFont, text: str = None):
        super().__init__(label, font, text)
        self._widget.setAlignment(Qt.AlignCenter)


class ComboBox(Widget):
    _widget: QComboBox

    def __init__(self, combo_box: QComboBox, font: QFont):
        super().__init__(combo_box, font)
        self._widget.setStyleSheet("background-color:rgb(255, 255, 255)")


class Table(Widget):
    _widget: QTableWidget

    def __init__(self, table: QTableWidget, font: QFont):
        super().__init__(table, font)


def label_wrapper(label: QLabel, text: str = None) -> None:
    FONT_SIZE = 14
    FONT_TYPE = "Arial"

    font = QFont(FONT_TYPE, FONT_SIZE)

    Label(label, font, text=text)


def combo_box_wrapper(combo_box: QComboBox) -> None:
    FONT_SIZE = 12
    FONT_TYPE = "Arial"

    font = QFont(FONT_TYPE, FONT_SIZE)

    ComboBox(combo_box, font)


def title_label_wrapper(label: QLabel, text: str = None) -> None:
    FONT_SIZE = 18
    FONT_TYPE = "Arial Rounded MT Bold"

    font = QFont(FONT_TYPE, FONT_SIZE)
    font.setBold(True)

    TitleLabel(label, font, text=text)


def table_wrapper(table: QTableWidget) -> None:
    FONT_SIZE = 12
    FONT_TYPE = "Arial"

    font = QFont(FONT_TYPE, FONT_SIZE)

    Table(table, font)


def set_dropbox(box: QComboBox, items: list[str], *, all_option: bool = True) -> None:
    if all_option:
        items.insert(0, "All")

    box.addItems(items)


def set_table(table: QTableWidget, data: pd.DataFrame) -> None:
    data_dim = data.shape
    columns = data_dim[1]
    rows = data_dim[0]

    table.setRowCount(rows)
    table.setColumnCount(columns)

    for row_num, row in enumerate(data.itertuples()):
        row_no_index = row[1:]

        for col_num, value in enumerate(row_no_index):
            if isinstance(value, QWidget):
                table.setCellWidget(row_num, col_num, value)
            else:
                table.setItem(row_num, col_num, QTableWidgetItem(str(value)))

    table.setHorizontalHeaderLabels(data.columns)
    table.setVerticalHeaderLabels([str(idx) for idx in data.index])


def create_msg(icon: QMessageBox, title: str, text: str) -> None:
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec_()

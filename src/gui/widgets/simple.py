from PyQt5.QtWidgets import QLabel, QComboBox, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pandas as pd
from abc import ABC, abstractmethod


def __set_widget(widget: QWidget, font: QFont) -> None:
    widget.setFont(font)

    return widget


class Widget(ABC):
    @classmethod
    @abstractmethod
    def get(cls) -> QWidget:
        pass

    @classmethod
    @abstractmethod
    def wrap(cls, widget: QWidget) -> None:
        pass

    @staticmethod
    def _set_widget(widget: QWidget, font: QFont) -> None:
        widget.setFont(font)

        return widget


class Label(Widget):
    FONT_SIZE = 14
    FONT_TYPE = "Arial"

    @classmethod
    def get(cls, text: str = None) -> QLabel:
        lbl = QLabel()
        cls.wrap(lbl, text=text)

        return lbl

    @classmethod
    def wrap(cls, label: QLabel, text: str = None) -> None:
        font = QFont(cls.FONT_TYPE, cls.FONT_SIZE)
        cls._set_widget(label, font)
        label.setText(text)


class Title(Label):
    FONT_SIZE = 18
    FONT_TYPE = "Arial Rounded MT Bold"

    @classmethod
    def wrap(cls, label: QLabel, text: str = None) -> None:
        font = QFont(cls.FONT_TYPE, cls.FONT_SIZE)
        font.setBold(True)
        cls._set_widget(label, font)

        label.setAlignment(Qt.AlignCenter)
        label.setText(text)


def get_combo_box() -> QComboBox:
    FONT_SIZE = 12
    FONT_TYPE = "Arial"
    font = QFont(FONT_TYPE, FONT_SIZE)

    box = QComboBox()
    __set_widget(box)
    box.setStyleSheet("background-color:rgb(255, 255, 255)")

    return box


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

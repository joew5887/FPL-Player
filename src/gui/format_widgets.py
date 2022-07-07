from PyQt5.QtWidgets import QLabel, QComboBox, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pandas as pd


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

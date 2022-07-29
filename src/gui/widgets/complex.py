from __future__ import annotations
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QLabel
)
from PyQt5.QtCore import Qt
from abc import abstractmethod
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from .simple import Title, Label, ComboBox, Table


class ComplexWidget(QWidget):
    def __init__(self, **kwargs):
        super().__init__()

        self.define_widgets(**kwargs)
        self.setup()
        self.add_widgets()

    @abstractmethod
    def define_widgets(self) -> None:
        pass

    @abstractmethod
    def setup(self) -> None:
        self.setMinimumHeight(700)

    @abstractmethod
    def add_widgets(self) -> None:
        pass


class WidgetWithTitle(ComplexWidget):
    def __init__(self, header_txt: str, main_widget: QWidget):
        super().__init__(header_txt=header_txt, main_widget=main_widget)

    @property
    def main(self) -> QWidget:
        return self.__main

    def define_widgets(self, **kwargs) -> None:
        self.__layout = QVBoxLayout()
        self._header_lbl = Label.get(kwargs["header_txt"])
        self.__main = kwargs["main_widget"]

    def setup(self) -> None:
        super().setup()

        self._header_lbl.setAlignment(Qt.AlignCenter)
        self._header_lbl.setMaximumHeight(100)

    def add_widgets(self) -> None:
        self.__layout.addWidget(self._header_lbl)
        self.__layout.addWidget(self.main)
        self.setLayout(self.__layout)


class ComplexWidgetWithTitle(WidgetWithTitle):
    def __init__(self, header_txt: str, main_widget: ComplexWidget):
        super().__init__(header_txt=header_txt, main_widget=main_widget)

    @property
    def main(self) -> ComplexWidget:
        return self.__main


class TitleWidget(ComplexWidget):
    def __init__(self, title_txt: str, *, left_txt: str, right_txt: str):
        super().__init__(title_txt=title_txt, left_txt=left_txt, right_txt=right_txt)

    def define_widgets(self, **kwargs) -> None:
        self.__layout = QHBoxLayout()
        self._title_lbl = Title.get(kwargs["title_txt"])
        self._info1_lbl = Label.get(kwargs["left_txt"])
        self._info2_lbl = Label.get(kwargs["right_txt"])

    def setup(self) -> None:
        self.__adjust_lbl_alignment()

    def add_widgets(self) -> None:
        self.__layout.addWidget(self._info1_lbl)
        self.__layout.addWidget(self._title_lbl)
        self.__layout.addWidget(self._info2_lbl)
        self.setLayout(self.__layout)

    def __adjust_lbl_alignment(self) -> None:
        self._info2_lbl.setAlignment(Qt.AlignRight)
        self._info1_lbl.setAlignment(Qt.AlignLeft)
        self._title_lbl.setAlignment(Qt.AlignHCenter)


class FilterBox(ComplexWidget):
    def __init__(self, filter_name: str, filters: list[str], *, all_option: bool = True):
        super().__init__(filter_name=filter_name, filters=filters, all_option=all_option)

    def define_widgets(self, **kwargs) -> None:
        self.__layout = QVBoxLayout()
        self._filter_lbl = Label.get(kwargs["filter_name"])
        self.filter_box = ComboBox.get(kwargs["filters"], kwargs["all_option"])

    def setup(self) -> None:
        self.setMinimumHeight(50)

        self._filter_lbl.setMaximumHeight(50)

        self.filter_box.currentIndexChanged.connect(
            self.reset_current_option
        )
        self.reset_current_option()

    def add_widgets(self) -> None:
        self.__layout.addWidget(self._filter_lbl)
        self.__layout.addWidget(self.filter_box)
        self.setLayout(self.__layout)

    def get_current_option(self) -> str:
        return self.__current_option

    def reset_current_option(self) -> None:
        self.__current_option = self.filter_box.currentText()


class TableWithTitle(ComplexWidget):
    def __init__(self, table_name: str, **kwargs):
        kwargs["table_name"] = table_name
        super().__init__(**kwargs)

    def define_widgets(self, **kwargs) -> None:
        self._layout = QVBoxLayout()
        self._title_lbl = Label.get(kwargs["table_name"])
        self._table = Table.get()

    def setup(self) -> None:
        super().setup()

        self._title_lbl.setAlignment(Qt.AlignCenter)

    def add_widgets(self) -> None:
        self._layout.addWidget(self._title_lbl)
        self._layout.addWidget(self._table)
        self.setLayout(self._layout)


class SearchTable(TableWithTitle):
    _filters: list[FilterBox]
    _sort: FilterBox

    def __init__(self, table_name: str, filters: list[FilterBox], sort_by: FilterBox):
        super().__init__(table_name, filters=filters, sort_by=sort_by)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)
        #self.__layout = QVBoxLayout()
        self.__filter_layout = QHBoxLayout()
        self._filters = kwargs["filters"]
        self._sort = kwargs["sort_by"]
        self.__filters_widget = QWidget()
        #self._table = Table.get()

    def setup(self) -> None:
        super().setup()

        for filter in self._filters:
            filter.filter_box.currentIndexChanged.connect(self.get_query)

        self._sort.filter_box.currentIndexChanged.connect(self.get_query)

        self.get_query()

    def add_widgets(self) -> None:
        for filter in self._filters:
            self.__filter_layout.addWidget(filter)

        self.__filters_widget.setLayout(self.__filter_layout)

        self._layout.addWidget(self._title_lbl)
        self._layout.addWidget(self.__filters_widget)
        self._layout.addWidget(self._table)
        self._layout.addWidget(self._sort)

        self.setLayout(self._layout)

    @abstractmethod
    def get_query(self) -> None:
        print("table")
        for filter in self._filters:
            print(filter.get_current_option())
        print("")


class GraphWithTitle(ComplexWidget):
    def __init__(self, graph_name: str, graph_widget: FigureCanvasQTAgg, x_labels: FilterBox, y_labels: FilterBox):
        super().__init__(graph_name=graph_name, graph_widget=graph_widget,
                         x_labels=x_labels, y_labels=y_labels)

    def define_widgets(self, **kwargs) -> None:
        self._layout = QVBoxLayout()
        self._title_lbl = Label.get(kwargs["graph_name"])
        self._graph = kwargs["graph_widget"]

    def setup(self) -> None:
        super().setup()

        _graph: LineGraph
        self._graph.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        self._title_lbl.setAlignment(Qt.AlignCenter)

    def add_widgets(self) -> None:
        self._layout.addWidget(self._title_lbl)
        self._layout.addWidget(self._graph)
        self.setLayout(self._layout)


class LineGraph(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

    def plot(self, x: list, y: list) -> None:
        self.axes.plot(x, y)

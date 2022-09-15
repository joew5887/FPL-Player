from __future__ import annotations
from typing import Callable
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTableWidget, QLabel, QMainWindow
)
from PyQt5.QtCore import Qt, QThreadPool
from abc import ABC, abstractmethod
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pylab as plt
from matplotlib.figure import Figure
import matplotlib
from .thread import Thread
import pandas as pd
from .simple import Title, Label, ComboBox, Table


matplotlib.use("Qt5Agg")


class ComplexWidget(QWidget):
    def __init__(self, **kwargs):
        super().__init__()

        self.run(**kwargs)

    def run(self, **kwargs) -> None:
        self.define_widgets(**kwargs)
        self.setup()
        self.add_widgets()

    @abstractmethod
    def define_widgets(self, **kwargs) -> None:
        self._thread_pool = QThreadPool()

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def add_widgets(self) -> None:
        pass

    @abstractmethod
    def get_default_header(self) -> QWidget:
        return QWidget()

    @abstractmethod
    def get_default_footer(self) -> QWidget:
        return QWidget()


class ContentWidget(ComplexWidget):
    def setup(self) -> None:
        super().setup()

        self.setMinimumHeight(700)


class AddHeaders(ComplexWidget):
    __header: QWidget
    __main: QWidget
    __footer: QWidget

    def __init__(self, main_widget: QWidget, *, header: QWidget = None, footer: QWidget = None):
        super().__init__(header_widget=header,
                         main_widget=main_widget, footer_widget=footer)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)

        self.__layout = QVBoxLayout()
        self.__header = kwargs["header_widget"]
        self.__main = kwargs["main_widget"]
        self.__footer = kwargs["footer_widget"]

    def setup(self) -> None:
        super().setup()

        if self.__header is not None:
            self.__header.setMaximumHeight(100)

        if self.__footer is not None:
            self.__footer.setMaximumHeight(100)

        self.setMinimumHeight(700)

    def add_widgets(self) -> None:
        super().add_widgets()

        self.__layout.addWidget(self.__header)
        self.__layout.addWidget(self.__main)
        self.__layout.addWidget(self.__footer)
        self.setLayout(self.__layout)


class AddDefaultHeaders(AddHeaders):
    def __init__(self, main_widget: ComplexWidget):
        super().__init__(main_widget, header=main_widget.get_default_header(),
                         footer=main_widget.get_default_footer())


class TitleWidget(ComplexWidget):
    def __init__(self, title_txt: str, *, left_txt: str = None, right_txt: str = None):
        super().__init__(title_txt=title_txt, left_txt=left_txt, right_txt=right_txt)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)

        self.__layout = QHBoxLayout()
        self._title_lbl = Title.get(kwargs["title_txt"])
        self._info1_lbl = Label.get(kwargs["left_txt"])
        self._info2_lbl = Label.get(kwargs["right_txt"])

    def setup(self) -> None:
        super().setup()

        self.__adjust_lbl_alignment()

    def add_widgets(self) -> None:
        super().add_widgets()

        self.__layout.addWidget(self._info1_lbl)
        self.__layout.addWidget(self._title_lbl)
        self.__layout.addWidget(self._info2_lbl)
        self.setLayout(self.__layout)

    def __adjust_lbl_alignment(self) -> None:
        self._info2_lbl.setAlignment(Qt.AlignRight)
        self._info1_lbl.setAlignment(Qt.AlignLeft)
        self._title_lbl.setAlignment(Qt.AlignHCenter)


class RefineSearchWidget(ComplexWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)

        self._filter_lbl = Label.get(kwargs["filter_name"])

    def setup(self) -> None:
        super().setup()

        self.setMinimumHeight(50)
        self.setMaximumHeight(150)

        self._filter_lbl.setMaximumHeight(50)

        self.filter_changed(self.set_current_option)
        self.set_current_option()

    @abstractmethod
    def filter_changed(self, action: Callable) -> None:
        return

    @abstractmethod
    def _access_value(self) -> str:
        return

    def get_current_option(self) -> str:
        return self.__current_option

    def set_current_option(self) -> None:
        self.__current_option = self._access_value()


class FilterBox(RefineSearchWidget):
    def __init__(self, filter_name: str, filters: list[str], *, all_option: bool = True):
        super().__init__(filter_name=filter_name, filters=filters, all_option=all_option)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets(**kwargs)

        self.__layout = QVBoxLayout()
        self._filter_box = ComboBox.get(
            kwargs["filters"], kwargs["all_option"])

    def add_widgets(self) -> None:
        super().add_widgets()

        self.__layout.addWidget(self._filter_lbl)
        self.__layout.addWidget(self._filter_box)
        self.setLayout(self.__layout)

    def filter_changed(self, action: Callable) -> None:
        self._filter_box.currentIndexChanged.connect(action)

    def _access_value(self) -> None:
        return self._filter_box.currentText()


class SearchTable(ContentWidget):
    _filters: list[FilterBox]
    _sort: FilterBox

    def __init__(self, filters: list[RefineSearchWidget], sort_by: RefineSearchWidget):
        super().__init__(filters=filters, sort_by=sort_by)

    def define_widgets(self, **kwargs) -> None:
        super().define_widgets()

        self.__layout = QVBoxLayout()
        self._filter_layout = QHBoxLayout()
        self._filters = kwargs["filters"]
        self._sort = kwargs["sort_by"]
        self.__filters_widget = QWidget()
        self._table = Table.get()
        self._output_data = pd.DataFrame()

    def setup(self) -> None:
        super().setup()

        for filter in self._filters:
            filter.filter_changed(self.update_query)

        if self._sort is not None:
            self._sort.filter_changed(self.update_query)

        self.update_query()

    def add_widgets(self) -> None:
        super().add_widgets()

        for filter_ in self._filters:
            self._filter_layout.addWidget(filter_)

        self.__filters_widget.setLayout(self._filter_layout)

        # self.__layout.addWidget(self._title_lbl)
        self.__layout.addWidget(self.__filters_widget)
        self.__layout.addWidget(self._table)

        if self._sort is not None:
            self.__layout.addWidget(self._sort)

        self.setLayout(self.__layout)

    @abstractmethod
    def update_query(self) -> None:
        return

    def update_table(self, df: pd.DataFrame) -> None:
        Table.set_data(self._table, df)


class GraphWidget(ContentWidget):
    def __init__(self):
        super().__init__()

    def define_widgets(self, **kwargs) -> None:
        self._layout = QVBoxLayout()
        self._plot_widget = QWidget()
        self._plot_layout = QHBoxLayout()

        self._figure, self._subplots = plt.subplots()
        self._graph = FigureCanvasQTAgg(self._figure)

    def setup(self) -> None:
        super().setup()

        self.draw_graph()

    def add_widgets(self) -> None:
        self._layout.addWidget(self._graph)
        self._layout.addWidget(NavigationToolbar(self._graph, self))
        self.setLayout(self._layout)

    @abstractmethod
    def draw_graph(self) -> None:
        pass


class LineGraph(GraphWidget):
    def draw_graph(self) -> None:
        self._subplots.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40], "bo")

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTableWidget
)
from PyQt5.QtCore import Qt
from abc import abstractmethod
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
        pass

    @abstractmethod
    def add_widgets(self) -> None:
        pass


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


class SearchTable(ComplexWidget):
    _filters: list[FilterBox]
    _sort: FilterBox

    def __init__(self, filters: list[FilterBox], sort_by: FilterBox):
        super().__init__(filters=filters, sort_by=sort_by)

    def define_widgets(self, **kwargs) -> None:
        self.__layout = QVBoxLayout()
        self.__filter_layout = QHBoxLayout()
        self._filters = kwargs["filters"]
        self._sort = kwargs["sort_by"]
        self.__filters_widget = QWidget()
        self._table = Table.get()

    def setup(self) -> None:
        for filter in self._filters:
            filter.filter_box.currentIndexChanged.connect(self.get_query)

        self._sort.filter_box.currentIndexChanged.connect(self.get_query)

        self.get_query()

    def add_widgets(self) -> None:
        for filter in self._filters:
            self.__filter_layout.addWidget(filter)

        self.__filters_widget.setLayout(self.__filter_layout)

        self.__layout.addWidget(self.__filters_widget)
        self.__layout.addWidget(self._table)
        self.__layout.addWidget(self._sort)

        self.setLayout(self.__layout)

    @abstractmethod
    def get_query(self) -> None:
        print("table")
        for filter in self._filters:
            print(filter.get_current_option())
        print("")

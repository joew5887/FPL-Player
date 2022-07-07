from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from .titles import Title, FPLWindowTitle
from .widgets import VerticalTabWidget
from typing import Callable


class DefaultWindow(QMainWindow):
    def __init__(self, title_widget: Title, menu_options: dict[str, Callable[..., QWidget]]):
        super().__init__()

        self.__title_widget = title_widget
        self.__content_widget = VerticalTabWidget(menu_options)
        self._set_widgets()
        self.show()

    def _set_widgets(self) -> None:
        self.__window = self.__get_window()
        self.__screen_layout = QVBoxLayout()

        self.__screen_layout.addWidget(self.__title_widget)
        self.__screen_layout.addWidget(self.__content_widget)

        self.__window.setLayout(self.__screen_layout)
        self.setCentralWidget(self.__window)
        self.resize(1200, 800)

    def __get_window(self) -> QWidget:
        window = QWidget()

        return window


class FPLWindow(DefaultWindow):
    def __init__(self):
        super().__init__(FPLWindowTitle(), {t: lambda _=True, x=t: self.label_test(x) for t in ["Home", "Players",
                                                                                                "Teams", "Fixtures", "Events"]})

    def label_test(self, txt: str) -> QLabel:
        x = QLabel()
        x.setText(txt)

        return x

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
from .thread import set_complex_widget
from .widgets import TitleWidget, HomeWindowTitle
from time import sleep


class DefaultWindow(QMainWindow):
    DIST_X = 1200
    DIST_Y = 800

    def __init__(self, title_widget: TitleWidget, content_widget: QWidget, dist_x: int = DIST_X, dist_y: int = DIST_Y):
        super().__init__()

        self.__title_widget = title_widget
        set_complex_widget(self.__title_widget)
        self.__content_widget = content_widget

        self._set_widgets()
        self.__set_size(dist_x, dist_y)
        self.show()

    def _set_widgets(self) -> None:
        self.__window = self.__get_window()
        self.__screen_layout = QVBoxLayout()

        self.__screen_layout.addWidget(self.__title_widget)
        self.__screen_layout.addWidget(self.__content_widget)

        self.__window.setLayout(self.__screen_layout)
        self.setCentralWidget(self.__window)

    def __set_size(self, dist_x: int, dist_y: int) -> None:
        self.resize(dist_x, dist_y)

    def __get_window(self) -> QWidget:
        window = QWidget()

        return window


class HomeWindow(DefaultWindow):
    def __init__(self):
        main_widget = self.__get_home()
        super().__init__(HomeWindowTitle(), main_widget)

    def __get_home(self) -> QWidget:
        x = QTabWidget()
        for i in ["Home", "Players", "Teams", "Fixtures", "Events"]:
            z = QLabel()
            z.setText(i)
            x.addTab(z, i)

        return x


class ElementWindow(DefaultWindow):
    pass

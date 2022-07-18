from abc import abstractmethod
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from .widgets import TitleWidget


class Window(QMainWindow):
    def __init__(self, dist_x: int, dist_y: int, **kwargs):
        super().__init__()

        self.define_widgets(**kwargs)
        self.setup(dist_x, dist_y)
        self.add_widgets()

        self.show()

    @abstractmethod
    def define_widgets(self) -> None:
        pass

    @abstractmethod
    def setup(self, dist_x: int, dist_y: int) -> None:
        self.resize(dist_x, dist_y)

    @abstractmethod
    def add_widgets(self) -> None:
        pass


class DefaultWindow(Window):
    DIST_X = 1600
    DIST_Y = 1200

    _content_widget: QWidget
    _title_widget: TitleWidget

    def __init__(self, title_widget: TitleWidget, content_widget: QWidget, dist_x: int = DIST_X, dist_y: int = DIST_Y):
        super().__init__(dist_x, dist_y, title_widget=title_widget,
                         content_widget=content_widget)

    def define_widgets(self, **kwargs) -> None:
        self.__window = self.__get_window()
        self.__screen_layout = QVBoxLayout()
        self._content_widget = kwargs["content_widget"]
        self._title_widget = kwargs["title_widget"]

    def setup(self, dist_x: int, dist_y: int) -> None:
        super().setup(dist_x, dist_y)

    def add_widgets(self) -> None:
        self.__screen_layout.addWidget(self._title_widget)
        self.__screen_layout.addWidget(self._content_widget)

        self.__window.setLayout(self.__screen_layout)
        self.setCentralWidget(self.__window)

    def __get_window(self) -> QWidget:
        window = QWidget()

        return window

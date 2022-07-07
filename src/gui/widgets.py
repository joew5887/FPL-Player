from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea
)
from PyQt5.QtGui import QFont
from typing import Callable


class VerticalMenu(QScrollArea):
    __tab_to_button: dict[str, QPushButton]

    def __init__(self):
        super().__init__()
        self.__layout = self._default_layout()
        self.__tab_to_button = dict()

        self.setLayout(self.__layout)

    def add_tab(self, tab_name: str) -> None:
        button = self.__new_button(tab_name)
        self.__layout.addWidget(button)
        self.__tab_to_button[tab_name] = button

    def remove_tab(self, tab_name: str) -> None:
        self.__layout.removeWidget(self.__tab_to_button[tab_name])
        del self.__tab_to_button[tab_name]

    def set_current_tab(self, tab_name: str) -> None:
        self.__button_clicked(tab_name)

    def get_button(self, tab_name: str) -> QPushButton:
        return self.__tab_to_button.get(tab_name)

    def __new_button(self, tab_name: str) -> QPushButton:
        button = QPushButton()
        button.setText(tab_name)
        button.clicked.connect(lambda: self.__button_clicked(tab_name))

        return button

    def __button_clicked(self, clicked_tab_name: str) -> None:
        for tab_name, button in self.__tab_to_button.items():
            if clicked_tab_name == tab_name:
                button.setFont(VerticalMenu._clicked_font())
            else:
                button.setFont(VerticalMenu._not_clicked_font())

    def _default_layout(self) -> QVBoxLayout:
        return QVBoxLayout()

    @staticmethod
    def _not_clicked_font() -> QFont:
        font = QFont()

        return font

    @staticmethod
    def _clicked_font() -> QFont:
        font = QFont()
        font.setUnderline(True)

        return font


class HorizontalMenu(VerticalMenu):
    def __init__(self):
        super().__init__()

    def _default_layout(self) -> QHBoxLayout:
        return QHBoxLayout()


class VerticalTabWidget(QWidget):
    __tab_to_action: dict[str, Callable[..., QWidget]]

    def __init__(self, tab_to_action: dict[str, Callable[..., QWidget]]):
        super().__init__()
        self.__tab_to_action = tab_to_action

        self.__layout = self._screen_layout()
        self.__menu_widget = self._menu_widget()
        self.__current_widget = QWidget()

        self.setLayout(self.__layout)
        self.__layout.addWidget(self.__menu_widget)
        self.__layout.addWidget(self.__current_widget)

        self.__set_tabs()
        self._set_widget_limits()

    @property
    def current_widget(self) -> QWidget:
        return self.__current_widget

    @current_widget.setter
    def current_widget(self, new_widget: QWidget) -> None:
        self.__layout.replaceWidget(self.__current_widget, new_widget)
        self.__current_widget.deleteLater()

        self.__current_widget = new_widget

    def add_tab(self, widget_func: Callable[..., QWidget], tab_name: str) -> None:
        self.__menu_widget.add_tab(tab_name)
        self.__tab_to_action[tab_name] = widget_func

        button = self.__menu_widget.get_button(tab_name)
        button.clicked.connect(
            lambda: self.__get_widget(tab_name))

    def remove_tab(self, tab_name: str) -> None:
        self.__menu_widget.remove_tab(tab_name)
        del self.__tab_to_action[tab_name]

    def set_current_tab(self, tab_name: str) -> None:
        self.__menu_widget.set_current_tab(tab_name)
        self.__get_widget(tab_name)

    def __get_widget(self, tab_name: str) -> None:
        action = self.__tab_to_action[tab_name]
        new_widget = action()
        self.current_widget = new_widget

    def __set_tabs(self) -> None:
        for tab_name, action in self.__tab_to_action.items():
            self.add_tab(action, tab_name)

        self.set_current_tab(list(self.__tab_to_action.keys())[0])

    def _screen_layout(self) -> QHBoxLayout:
        return QHBoxLayout()

    def _menu_widget(self) -> VerticalMenu:
        return VerticalMenu()

    def _set_widget_limits(self) -> None:
        self.setMaximumWidth(300)
        self.setMinimumHeight(100)


class HorizontalTabWidget(VerticalTabWidget):
    def __init__(self, tab_to_action: dict[str, Callable[..., QWidget]]):
        super().__init__(tab_to_action)

    def _menu_widget(self) -> HorizontalMenu:
        return HorizontalMenu()

    def _screen_layout(self) -> QVBoxLayout:
        return QVBoxLayout()

    def _set_widget_limits(self) -> None:
        return


def create_msg(icon: QMessageBox, title: str, text: str) -> None:
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec_()

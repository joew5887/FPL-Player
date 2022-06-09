from fpld.elements.element import Element
from .parent import FPLWindow, title_label_wrapper
from fpld import Player


class FPLElemWindow(FPLWindow):
    def __init__(self, element: Element):
        self.__element = element
        super().__init__("element.ui")
        self.show()

    def _set_widgets(self) -> None:
        self.title_lbl.setText(str(self.__element))


class PlayerScrn(FPLElemWindow):
    def __init__(self, player: Player):
        super().__init__(player)

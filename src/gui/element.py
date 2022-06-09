from fpld.elements.element import Element
from .parent import FPLWindow, title_label_wrapper
import fpld


class FPLElemWindow(FPLWindow):
    def __init__(self, element: Element):
        self.__element = element
        super().__init__("element.ui")
        self.show()

    def _set_widgets(self) -> None:
        self.title_lbl.setText(str(self.__element))


class PlayerScrn(FPLElemWindow):
    def __init__(self, player: fpld.Player):
        super().__init__(player)


class TeamScrn(FPLElemWindow):
    def __init__(self, team: fpld.Team):
        super().__init__(team)


class PositionScrn(FPLElemWindow):
    def __init__(self, position: fpld.Position):
        super().__init__(position)

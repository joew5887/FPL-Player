from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QFont


GUI_STEM = ".//lib//"


class FPLWindow(QMainWindow):
    def __init__(self, window_name: str) -> None:
        super().__init__()
        self.ui = loadUi(GUI_STEM + window_name, self)
        self.show()


class FPLSubWindow(FPLWindow):
    TITLE_FONT = QFont("Arial Rounded MT Bold", 20)

    def __init__(self, window_name: str) -> None:
        super().__init__(window_name)
        # self.back_btn.clicked.connect(self.close)
        # self.title_lbl.setFont(type(self).TITLE_FONT)

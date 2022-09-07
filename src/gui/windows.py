from PyQt5.QtWidgets import QMainWindow, QWidget


class Window(QMainWindow):
    """Default Window class for FPL GUI.

    Inherits 'QMainWindow'.
    """
    # Default GUI dimensions
    DIST_X = 1600
    DIST_Y = 1200

    def __init__(self, widget: QWidget, dist_x: int = DIST_X, dist_y: int = DIST_Y):
        super().__init__()

        self.setup(dist_x, dist_y)
        self.setCentralWidget(widget)

    def setup(self, dist_x: int, dist_y: int) -> None:
        self.resize(dist_x, dist_y)

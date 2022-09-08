from fplgui import Home
from gui.windows import Window
from gui.widgets import AddDefaultHeaders
import sys
from PyQt5.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    home = Window(AddDefaultHeaders(Home()))
    home.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

from fplgui import Home
from gui.windows import Window
import sys
from PyQt5.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    home = Window(Home.add_default_headers())
    home.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

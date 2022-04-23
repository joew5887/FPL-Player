from multiprocessing import Event
import gui
import sys
from PyQt5.QtWidgets import QApplication
import fpld


def main() -> None:
    app = QApplication(sys.argv)
    home = gui.HomeScrn()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

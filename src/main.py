from gui import FPLWindow
import sys
from PyQt5.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    home = FPLWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

from gui import HomeScrn
import sys
from PyQt5.QtWidgets import QApplication


def main() -> None:
    app = QApplication(sys.argv)
    home = HomeScrn()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

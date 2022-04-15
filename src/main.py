import gui
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home = gui.HomeScrn()
    sys.exit(app.exec_())

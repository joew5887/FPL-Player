from .parent import FPLWindow


class HomeScrn(FPLWindow):
    def __init__(self):
        super().__init__("home.ui")
        self.show()

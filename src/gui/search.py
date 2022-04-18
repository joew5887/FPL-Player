from .parent import FPLWindow


class SearchScrn(FPLWindow):
    def __init__(self):
        super().__init__("search.ui")
        self.show()

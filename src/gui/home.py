from .parent import FPLWindow
from .search import SearchScrn


class HomeScrn(FPLWindow):
    def __init__(self):
        super().__init__("home.ui")

    def _set_widgets(self) -> None:
        self.search_btn.clicked.connect(self.open_search)

    def open_search(self) -> None:
        page = SearchScrn()
        page.show()

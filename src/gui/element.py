from fpld.elements.element import Element
from .parent import FPLWindow, combo_box_wrapper, title_label_wrapper
import fpld
import pyqtgraph as pg
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QComboBox, QHBoxLayout


class FPLElemWindow(FPLWindow):
    info_tab: QTabWidget

    def __init__(self, element: Element):
        self._element = element
        super().__init__("element.ui")
        self.show()

    def _set_widgets(self) -> None:
        self.info_tab.clear()
        self.title_lbl.setText(str(self._element))


class PlayerScrn(FPLElemWindow):
    _element: fpld.Player
    graph: pg.PlotWidget

    def __init__(self, player: fpld.Player):
        super().__init__(player)

    def _set_widgets(self) -> None:
        super()._set_widgets()
        bar = self._element.in_full()
        self.__graph_tab(bar.history.categorical_vars,
                         bar.history.continuous_vars)

    def __graph_tab(self, x_choices: list[str], y_choices: list[str]) -> None:
        tab = QWidget()
        self.__layout = QVBoxLayout(tab)
        self.graph = pg.PlotWidget()

        edit_graph_widget = self.__get_edit_graph_widget(x_choices, y_choices)
        self.__layout.addWidget(edit_graph_widget)
        self.graph.setBackground('w')
        self.__layout.addWidget(self.graph)
        self.info_tab.addTab(tab, "History")

    def draw(self, x_var: str, y_var: str) -> None:
        bar = self._element.in_full()
        x = getattr(bar.history, x_var)
        y = getattr(bar.history, y_var)
        if x_var == "opponent_team":
            l = [t.short_name for t in x.values]
        else:
            l = [str(i) for i in x.values]
        x_dict = dict(enumerate(l))
        stringaxis = pg.AxisItem(orientation="bottom")
        stringaxis.setTicks([x_dict.items()])
        pen = pg.mkPen(color=(255, 0, 0), width=5)
        self.__layout.removeWidget(self.graph)
        self.graph = pg.PlotWidget(axisItems={"bottom": stringaxis})
        self.graph.plot(list(x_dict.keys()), y.values, pen=pen)
        self.__layout.addWidget(self.graph)

    def __get_edit_graph_widget(self, x_choices: list[str], y_choices: list[str]) -> QWidget:
        x_combo_box = self.__set_combo_box(x_choices)
        y_combo_box = self.__set_combo_box(y_choices)

        x_combo_box.currentIndexChanged.connect(
            lambda: self.draw(x_combo_box.currentText(), y_combo_box.currentText()))
        y_combo_box.currentIndexChanged.connect(
            lambda: self.draw(x_combo_box.currentText(), y_combo_box.currentText()))

        edit_graph_widget = QWidget()
        edit_graph_layout = QHBoxLayout(edit_graph_widget)
        edit_graph_layout.addWidget(x_combo_box)
        edit_graph_layout.addWidget(y_combo_box)

        return edit_graph_widget

    def __set_combo_box(self, data: list[str]) -> QComboBox:
        combo_box = QComboBox()
        combo_box_wrapper(combo_box)
        combo_box.addItems(data)

        return combo_box


class TeamScrn(FPLElemWindow):
    def __init__(self, team: fpld.Team):
        super().__init__(team)


class PositionScrn(FPLElemWindow):
    def __init__(self, position: fpld.Position):
        super().__init__(position)

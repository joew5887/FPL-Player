from typing import Any, Callable
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QRunnable
from traceback import format_tb  # Creating error message on loading screen.
import pandas as pd


class Signals(QObject):
    finished = pyqtSignal(bool)
    return_value = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(Exception)


class Thread(QRunnable):
    def __init__(self, task: Callable[..., Any]):
        super().__init__()
        self.signal = Signals()
        self.__task = task

    @pyqtSlot()
    def run(self):
        try:
            value = self.__task()
        except Exception as err:
            self.signal.error.emit(err)
        else:
            self.signal.return_value.emit(value)

        self.signal.finished.emit(True)

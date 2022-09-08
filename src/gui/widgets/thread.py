from types import NoneType
from typing import Any, Callable
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QRunnable, QThreadPool
from traceback import format_tb  # Creating error message on loading screen.
from PyQt5.uic import loadUi
from abc import abstractmethod


class Signals(QObject):
    finished = pyqtSignal(bool)
    #return_value = pyqtSignal(Any)
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
        '''else:
            self.signal.return_value.emit(value)'''

        self.signal.finished.emit(True)

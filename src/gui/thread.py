from typing import Callable
from .parent import FPLWindow, set_text_label
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QProgressBar, QLabel


class _LoadingScreen(FPLWindow):
    info_lbl: QLabel
    progress_bar: QProgressBar

    def __init__(self) -> None:
        super().__init__("loading.ui")

    def _set_widgets(self) -> None:
        set_text_label(self.info_lbl, "foo")
        self.title_lbl.setText("Loading")

    @pyqtSlot(float)
    def update_progress(self, percent: float) -> None:
        self.progress_bar.setValue(int(percent))

    @pyqtSlot(str)
    def update_info(self, info: str) -> None:
        self.info_lbl.setText(info)


class _WorkerThread(QThread):
    finished_signal = pyqtSignal()
    info_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(float)
    error_signal = pyqtSignal(Exception)

    def __init__(self, loading_scrn: _LoadingScreen, tasks: dict[str, Callable]):
        super().__init__(loading_scrn)
        self.__tasks = tasks

    def run(self) -> None:
        tasks_completed = 0
        num_tasks = len(self.__tasks)

        for title, task in self.__tasks.items():
            self.info_signal.emit(title)
            percent_on = (tasks_completed / num_tasks) * 100
            self.progress_signal.emit(percent_on)

            try:
                task()
            except Exception as error:
                self.error_signal.emit(error)
            else:
                tasks_completed += 1

        percent_on = 1
        self.progress_signal.emit(percent_on)

        self.__task_finished()

    def __task_finished(self) -> None:
        self.finished_signal.emit()


class LongTask(QObject):
    def __init__(self, tasks: dict[str, Callable]):
        super().__init__()
        self.__tasks = tasks
        self.__scrn = _LoadingScreen()
        self.fini = False

    def start(self) -> None:
        self.__thread = _WorkerThread(self.__scrn, self.__tasks)
        self.__link_signals()
        self.__scrn.show()
        self.__thread.start()

    def __link_signals(self) -> None:
        self.__thread.info_signal.connect(self.__scrn.update_info)
        self.__thread.progress_signal.connect(self.__scrn.update_progress)
        self.__thread.error_signal.connect(self.__error_raised)

        self.__thread.finished_signal.connect(lambda: self.__exit_task(True))

    def __error_raised(self, error) -> None:
        pass

    def __exit_task(self, task_successful: bool) -> None:
        self.fini = True
        self.__scrn.close()
        self.__end_thread()

    def __end_thread(self) -> None:
        self.__thread.quit()
        self.__thread.deleteLater()

    def is_running(self) -> bool:
        return self.__thread.isRunning()

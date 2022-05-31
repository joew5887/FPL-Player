from typing import Callable
from .parent import FPLWindow, set_text_label, create_msg
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QProgressBar, QLabel


class _LoadingScrn(FPLWindow):
    info_lbl: QLabel
    progress_bar: QProgressBar

    def __init__(self) -> None:
        super().__init__("loading.ui")

    def _set_widgets(self) -> None:
        set_text_label(self.info_lbl, "foo")
        self.title_lbl.setText("Loading")

    @pyqtSlot(float)
    def update_progress(self, percent: float) -> None:
        """Update progress bar to show status of task.

        Parameters
        ----------
        percent : float
            New percent of progress.
        """
        self.progress_bar.setValue(int(percent))

    @pyqtSlot(str)
    def update_info(self, info: str) -> None:
        """String description of the task the worker thread is currently on.

        Parameters
        ----------
        info : str
            String description of current task.
        """
        self.info_lbl.setText(info)


class _WorkerThread(QThread):
    finished_signal = pyqtSignal()
    info_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(float)
    error_signal = pyqtSignal(Exception)

    def __init__(self, loading_scrn: _LoadingScrn, tasks: dict[str, Callable]):
        super().__init__(loading_scrn)
        self.__tasks = tasks

    def run(self) -> None:
        """Runs thread and calculates percent of progress.
        """
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
        """Runs any extra code when the tasks have been completed.
        """
        self.finished_signal.emit()


class LongTask(QObject):
    def __init__(self, tasks: dict[str, Callable], end_task: Callable):
        super().__init__()
        self.__tasks = tasks
        self.__end_task = end_task
        self.__scrn = _LoadingScrn()

    def start(self) -> None:
        """Run the thread and open loading screen.
        """
        self.__thread = _WorkerThread(self.__scrn, self.__tasks)
        self.__link_signals()
        self.__scrn.show()
        self.__thread.start()

    def __link_signals(self) -> None:
        """Sets up all signals.
        """
        self.__thread.info_signal.connect(self.__scrn.update_info)
        self.__thread.progress_signal.connect(self.__scrn.update_progress)
        self.__thread.error_signal.connect(self.__error_raised)

        self.__thread.finished_signal.connect(self.__exit_task)

    def __error_raised(self, error: Exception) -> None:
        """If an error is raised, the task is not completed.

        Parameters
        ----------
        error : Exception
            Type of error raised.
        """
        # create_msg()
        self.__scrn.close()
        self.__end_thread()

    def __exit_task(self) -> None:
        """Exit task after it has been sucessfully completed.
        """
        self.__scrn.close()
        self.__end_thread()
        self.__end_task()

    def __end_thread(self) -> None:
        """Kill the worker thread.
        """
        self.__thread.quit()
        self.__thread.deleteLater()

from aqt.qt import QObject, pyqtSignal


class WorkerSignals(QObject):

    cancel = pyqtSignal()
    error = pyqtSignal(tuple)
    finished = pyqtSignal()
    progress = pyqtSignal(tuple)
    result = pyqtSignal(object)



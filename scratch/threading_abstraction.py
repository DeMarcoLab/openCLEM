from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QProgressBar, QVBoxLayout, QWidg
import time
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

@abstractmethod
class LiveImaging(QThread):
    finished = pyqtSignal()
    image_finished = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(LiveImaging, self).__init__(parent)

    def run(self):
        raise NotImplementedError


@abstractmethod
class LiveImagingRunner(QMainWindow):
    def __init__(self, par=None):
        super(LiveImagingRunner, self).__init__()
        self.worker = LiveImaging()
        self.worker.finished.connect(self.handleFinished)
        self.worker.image_finished.connect(self.handleImageFinished)
        self.worker.start()

    def handleFinished(self):
        raise NotImplementedError

    def handleImageFinished(self, i):
        raise NotImplementedError

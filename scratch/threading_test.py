from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QProgressBar, QVBoxLayout, QWidget
import time
import numpy as np
import matplotlib.pyplot as plt

class Worker(QThread):
    finished = pyqtSignal()
    imaging_finished = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)

    def run(self):
        for i in range(100):
            time.sleep(1)
            self.imaging_finished.emit(np.random.random(size=(1000,1000)))

        # do something
        self.finished.emit()

class Window(QMainWindow):
    def __init__(self, par=None):
        super(Window, self).__init__()
        self.par = par
        self.button = QPushButton('Start')
        self.progress = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.progress)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.button.clicked.connect(self.handleStart)
        self.show()

    def handleStart(self):
        self.worker = Worker()
        self.worker.finished.connect(self.handleFinished)
        self.worker.imaging_finished.connect(self.handleImagingFinished)
        self.worker.start()

    def handleFinished(self):
        print('finished')

    def handleImagingFinished(self, i):
        self.par.layers.clear()
        self.layer = self.par.add_image(i)

if __name__ == '__main__':
    import sys

    # napari
    import napari

    # embed in napari
    viewer = napari.Viewer()
    window = Window(par=viewer)
    viewer.window.add_dock_widget(window, area='right')

    app = QApplication(sys.argv)
    sys.exit(app.exec_())

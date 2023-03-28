import napari
import napari.utils.notifications
from PyQt5 import QtWidgets

from openclem.ui.qt import CLEMDetectorWidget

import numpy as np
from pathlib import Path
from openclem.structures import ImageSettings
from openclem.detector import Detector
from openclem.laser import LaserController, Laser
from openclem import constants, utils

class CLEMDetectorWidget(CLEMDetectorWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        detector: Detector = None,
        parent=None,
    ):
        super(CLEMDetectorWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.detector = detector 

        self.setup_connections()


    def setup_connections(self):

        print("setup_connections")
        print(self.detector)



    def closeEvent(self, event):
        self.viewer.layers.clear()
        event.accept()


def main():
    laser_controller, detector = utils.setup_hardware()

    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMDetectorWidget(viewer=viewer, detector=detector)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openclem import constants, utils
from openclem.detector import Detector
from openclem.laser import Laser, LaserController
from openclem.structures import ImageSettings, LaserControllerSettings, LaserSettings
from openclem.ui.qt import CLEMUI
from openclem.ui.CLEMLaserWidget import CLEMLaserWidget
from openclem.ui.CLEMDetectorWidget import CLEMDetectorWidget
from openclem.ui.CLEMImageWidget import CLEMImageWidget
from openclem.ui.CLEMObjectiveWidget import CLEMObjectiveWidget
from openclem import config as cfg
import os

from openclem.objective_stages.demo.demo import DemoObjective

class CLEMUI(CLEMUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(CLEMUI, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.lc, self.detector, self.obj = None, None, None
        self.image_widget, self.detector_widget, self.laser_widget = None, None, None
        self._hardware_connected = False

        self.lineEdit_config_filename.setText(os.path.join(cfg.BASE_PATH, "config", "system.yaml"))

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        self.pushButton_connect_hardware.clicked.connect(self.connect_hardware)

    def connect_hardware(self):
        config_filename = self.lineEdit_config_filename.text()

        if self._hardware_connected:
            self.lc.disconnect()
            self.detector.disconnect()
            self.lc, self.detector, self.obj = None, None, None
            logging.info("Disconnected from hardware")
            napari.utils.notifications.show_info("Disconnected from hardware")
        else:
            try:
                self.lc, self.detector, self.obj = utils.setup_session(config_path=config_filename)
                logging.info("Connected to hardware")
                napari.utils.notifications.show_info("Connected to hardware")
            except Exception as e:
                self.lc, self.detector, self.obj = None, None, None
                
                logging.error(f"Error connecting to hardware: {e}")
                napari.utils.notifications.show_error(
                    f"Error connecting to hardware: {e}"
                )

        self.update_ui()

    def update_ui(self):
        self._hardware_connected = self.lc is not None and self.detector is not None

        if self._hardware_connected:
            self.detector_widget = CLEMDetectorWidget(
                detector=self.detector, viewer=self.viewer
            )
            self.laser_widget = CLEMLaserWidget(lc=self.lc, viewer=self.viewer)
            self.image_widget = CLEMImageWidget(
                viewer=self.viewer,
                det_widget=self.detector_widget,
                laser_widget=self.laser_widget,
            )
            self.objective_widget = CLEMObjectiveWidget(viewer=self.viewer, 
                                                        objective=self.obj)

            self.tabWidget.addTab(self.image_widget, "Imaging")
            self.tabWidget.addTab(self.detector_widget, "Detector")
            self.tabWidget.addTab(self.laser_widget, "Lasers")
            self.tabWidget.addTab(self.objective_widget, "ObjectiveStage")

            self.pushButton_connect_hardware.setText("Connected")
            self.pushButton_connect_hardware.setStyleSheet("background-color: green")

            self.label_hardware_status.setText(
                "" + 
                f"Detector: {self.detector.name}" + 
                f"\nLaser Controller: {self.lc.name}"+ 
                f"\nLasers: {[laser for laser in self.lc.lasers]}" +
                f"\nObjective: {self.obj.name}"
            )

        else:
            self.tabWidget.removeTab(4)
            self.tabWidget.removeTab(3)
            self.tabWidget.removeTab(2)
            self.tabWidget.removeTab(1)

            self.pushButton_connect_hardware.setText("Connect Hardware")
            self.pushButton_connect_hardware.setStyleSheet("background-color: gray")

            self.label_hardware_status.setText("No Hardware Connected")

            if self.image_widget is None:
                return

            self.image_widget.deleteLater()
            self.detector_widget.deleteLater()
            self.laser_widget.deleteLater()
            self.objective_widget.deleteLater()


def main():
    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMUI(viewer=viewer)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

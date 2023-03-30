import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openclem import utils
from openclem.ui.qt import CLEMUI

from openclem.ui.CLEMImageWidget import CLEMImageWidget
from openclem.ui.CLEMHardwareWidget import CLEMHardwareWidget
from openclem import config as cfg
import os


class CLEMUI(CLEMUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(CLEMUI, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.microscope, self.settings = None, None
        self.image_widget, self.hardware_widget = None, None
        self._hardware_connected = False

        self.lineEdit_config_filename.setText(os.path.join(cfg.BASE_PATH, "config", "system.yaml"))

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        self.pushButton_connect_hardware.clicked.connect(self.connect_hardware)

    def connect_hardware(self):
        config_filename = self.lineEdit_config_filename.text()

        if self._hardware_connected:
            self.microscope.disconnect()
            self.microscope, self.settings = None, None
            logging.info("Disconnected from hardware")
            napari.utils.notifications.show_info("Disconnected from hardware")
        else:
            try:
                self.microscope, self.settings = utils.setup_session(config_path=config_filename)
                
                logging.info("Connected to hardware")
                napari.utils.notifications.show_info("Connected to hardware")
            except Exception as e:
                self.microscope, self.settings = None, None
                
                logging.error(f"Error connecting to hardware: {e}")
                napari.utils.notifications.show_error(
                    f"Error connecting to hardware: {e}"
                )

        self.update_ui()

    def update_ui(self):
        self._hardware_connected = self.microscope is not None

        if self._hardware_connected:
            
            self.hardware_widget = CLEMHardwareWidget(
                microscope=self.microscope,
                viewer=self.viewer,
            )
            self.image_widget = CLEMImageWidget(
                viewer=self.viewer,
                hardware_widget=self.hardware_widget,
            )
            
            self.tabWidget.addTab(self.image_widget, "Imaging")
            self.tabWidget.addTab(self.hardware_widget, "Hardware")
            self.pushButton_connect_hardware.setText("Connected")
            self.pushButton_connect_hardware.setStyleSheet("background-color: green")

            self.label_hardware_status.setText(
                "" + 
                f"Detector: {self.microscope._detector.name}" + 
                f"\nLaser Controller: {self.microscope._laser_controller.name}"+ 
                f"\nLasers: {[laser for laser in self.microscope._laser_controller.lasers]}" +
                f"\nObjective: {self.microscope._objective.name}" +
                f"\nSynchroniser: {self.microscope._synchroniser.name}"
            )

        else:
            self.tabWidget.removeTab(2)
            self.tabWidget.removeTab(1)
            

            self.pushButton_connect_hardware.setText("Connect Hardware")
            self.pushButton_connect_hardware.setStyleSheet("background-color: gray")

            self.label_hardware_status.setText("No Hardware Connected")

            if self.image_widget is None:
                return

            self.image_widget.deleteLater()
            self.hardware_widget.deleteLater()


def main():
    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMUI(viewer=viewer)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

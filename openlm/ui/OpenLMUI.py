import logging

import napari
import napari.utils.notifications
from PyQt5 import QtWidgets

from openlm import utils
from openlm.ui.qt import OpenLMUI

from openlm.ui.OpenLMImageWidget import OpenLMImageWidget
from openlm.ui.OpenLMHardwareWidget import OpenLMHardwareWidget
from openlm.ui.OpenLMSpinningDiskWidget import OpenLMSpinningDiskWidget
from openlm.ui.OpenLMCalibrationWidget import OpenLMCalibrationWidget
from openlm.ui.OpenLMCoordinateWidget import OpenLMCoordinateWidget
from openlm import config as cfg
import os

try:
    from fibsem import utils as fibsem_utils
    FIBSEM = True
except ImportError:
    FIBSEM = False


class OpenLMUI(OpenLMUI.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(OpenLMUI, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.microscope, self.settings = None, None
        self.image_widget, self.hardware_widget = None, None
        self._hardware_connected = False

        CFG_PATH = os.path.join(cfg.BASE_PATH, "config", "piedisc.yaml")
        # CFG_PATH = os.path.join(cfg.BASE_PATH, "config", "system.yaml")        
        self.lineEdit_config_filename.setText(CFG_PATH)

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

                if FIBSEM:
                    self.microscope.fibsem_microscope, self.microscope.fibsem_settings = fibsem_utils.setup_session()

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

            self.hardware_widget = OpenLMHardwareWidget(
                microscope=self.microscope,
                viewer=self.viewer,
            )
            self.image_widget = OpenLMImageWidget(
                viewer=self.viewer,
                hardware_widget=self.hardware_widget,
            )
            self.disk_widget = OpenLMSpinningDiskWidget(
                self.viewer
            )

            self.calibration_widget = OpenLMCalibrationWidget(
                microscope=self.microscope,
                viewer=self.viewer,
                parent=self
            )

            self.coordinate_widget = OpenLMCoordinateWidget(
                microscope=self.microscope.fibsem_microscope,
                settings=self.microscope.fibsem_settings,
                viewer=self.viewer,
            )   

            r = self.gridLayout.rowCount()
            c = self.gridLayout.columnCount()
            self.gridLayout.addWidget(self.image_widget, r, 0, 1, c)

            self.tabWidget.addTab(self.hardware_widget, "Hardware")
            self.tabWidget.addTab(self.disk_widget, "Spinning Disk")
            self.tabWidget.addTab(self.calibration_widget, "Calibration")
            self.tabWidget.addTab(self.coordinate_widget, "Coordinates")
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
            # remove self.image_widget from self.gridLayout
            self.gridLayout.removeWidget(self.image_widget)

            self.tabWidget.removeTab(4)
            self.tabWidget.removeTab(3)
            self.tabWidget.removeTab(2)
            self.tabWidget.removeTab(1)

            if self.image_widget is None:
                return

            self.image_widget.deleteLater()
            self.hardware_widget.deleteLater()
            self.disk_widget.deleteLater()
            self.calibration_widget.deleteLater()
            self.coordinate_widget.deleteLater()

            self.pushButton_connect_hardware.setText("Connect Hardware")
            self.pushButton_connect_hardware.setStyleSheet("background-color: gray")
            self.label_hardware_status.setText("No Hardware Connected")

    # on close
    def closeEvent(self, event):
        if self._hardware_connected:
            self.microscope.get_synchroniser().stop_sync()
            logging.info("Disconnected from hardware")
            napari.utils.notifications.show_info("Disconnected from hardware")

        event.accept()


def main():
    viewer = napari.Viewer(ndisplay=2)
    openlm_ui = OpenLMUI(viewer=viewer)
    viewer.window.add_dock_widget(
        openlm_ui, 
        area="right", 
        add_vertical_stretch=True, 
        name = "OpenLM"
    )
    napari.run()


if __name__ == "__main__":
    main()

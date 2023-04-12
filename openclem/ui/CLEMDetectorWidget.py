
import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openclem import constants, utils
from openclem.detector import Detector
from openclem.structures import (DetectorSettings, ExposureMode, ImageSettings,
                                 TriggerEdge, TriggerSource)
from openclem.ui.qt import CLEMDetectorWidget


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

        self.set_ui_from_detector_settings(self.detector.settings)

    def setup_connections(self):

        self.comboBox_exposure_mode.addItems([mode.name for mode in ExposureMode])
        self.comboBox_trigger_edge.addItems([edge.name for edge in TriggerEdge])
        self.comboBox_trigger_source.addItems([source.name for source in TriggerSource])

        self.pushButton_apply_detector_settings.clicked.connect(
            self.apply_detector_settings
        )

    def set_ui_from_detector_settings(self, det_settings: DetectorSettings):

        self.lineEdit_detector_name.setText(det_settings.name)
        self.doubleSpinBox_pixelsize.setValue(det_settings.pixel_size * constants.SI_TO_MICRO)
        self.spinBox_resolution_x.setValue(det_settings.resolution[1])
        self.spinBox_resolution_y.setValue(det_settings.resolution[0])
        self.comboBox_exposure_mode.setCurrentText(det_settings.exposure_mode.name)
        self.comboBox_trigger_edge.setCurrentText(det_settings.trigger_edge.name)
        self.comboBox_trigger_source.setCurrentText(det_settings.trigger_source.name)

    def get_detector_settings_from_ui(self):

        detector_settings = DetectorSettings(
            name = self.lineEdit_detector_name.text(),
            connection=None,
            pixel_size= self.doubleSpinBox_pixelsize.value() * constants.MICRO_TO_SI,
            resolution=[int(self.spinBox_resolution_y.value()), int(self.spinBox_resolution_x.value())],
            exposure_mode=ExposureMode[self.comboBox_exposure_mode.currentText()],
            trigger_edge=TriggerEdge[self.comboBox_trigger_edge.currentText()],
            trigger_source=TriggerSource[self.comboBox_trigger_source.currentText()],
        )

        return detector_settings

    def apply_detector_settings(self):

        logging.info(f"Applying detector settings")
        self.detector.settings = self.get_detector_settings_from_ui()

        napari.utils.notifications.show_info(
            f"Applied detector settings: {self.detector.settings}"
        )

def main():
    laser_controller, detector, obj = utils.setup_session()

    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMDetectorWidget(viewer=viewer, detector=detector)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

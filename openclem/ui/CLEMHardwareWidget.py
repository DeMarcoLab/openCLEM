import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openclem import constants, utils
from openclem.detector import Detector
from openclem.laser import Laser, LaserController
from openclem.microscope import LightMicroscope
from openclem.objective import ObjectiveStage
from openclem.structures import (DetectorSettings, ExposureMode, ImageSettings,
                                 LaserControllerSettings, LaserSettings,
                                 TriggerEdge, TriggerSource, ConnectionSettings, ConnectionType, SerialSettings, SocketSettings)
from openclem.ui.qt import CLEMHardwareWidget, CLEMObjectiveWidget


class CLEMHardwareWidget(CLEMHardwareWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        microscope: LightMicroscope,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(CLEMHardwareWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.microscope = microscope

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        logging.info("setup_connections")

        # detector
        self.comboBox_exposure_mode.addItems([mode.name for mode in ExposureMode])
        self.comboBox_trigger_edge.addItems([edge.name for edge in TriggerEdge])
        self.comboBox_trigger_source.addItems([source.name for source in TriggerSource])

        self.pushButton_apply_detector_settings.clicked.connect(
            self.apply_detector_settings
        )

        # laser controller
        self.pushButton_apply_laser_settings.clicked.connect(
            self.apply_laser_settings
        )

        self.comboBox_selected_laser.addItems(self.microscope._laser_controller.lasers.keys())
        self.comboBox_selected_laser.currentTextChanged.connect(self.update_ui)

        # objective
        self.pushButton_get_position.clicked.connect(self.get_position)
        self.pushButton_save_position.clicked.connect(self.save_position)
        self.pushButton_move_absolute.clicked.connect(self.move_absolute)
        self.pushButton_move_relative_down.clicked.connect(self.move_relative)
        self.pushButton_move_relative_up.clicked.connect(self.move_relative)

        # dont allow editing
        self.doubleSpinBox_current_position.setEnabled(False)
        self.doubleSpinBox_saved_position.setEnabled(False)

    def update_ui(self):
        self.set_ui_from_detector_settings(self.microscope._detector.settings)
        self.set_ui_from_objective(self.microscope._objective)

        self.set_ui_from_laser_controller_settings(self.microscope._laser_controller.settings)
        current_laser = self.comboBox_selected_laser.currentText()
        self.set_ui_from_laser_settings(self.microscope._laser_controller.lasers[current_laser].get())


    ### Detector
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
            connection=self.microscope.get_detector().settings.connection,
            pixel_size= self.doubleSpinBox_pixelsize.value() * constants.MICRO_TO_SI,
            resolution=[int(self.spinBox_resolution_y.value()), int(self.spinBox_resolution_x.value())],
            exposure_mode=ExposureMode[self.comboBox_exposure_mode.currentText()],
            trigger_edge=TriggerEdge[self.comboBox_trigger_edge.currentText()],
            trigger_source=TriggerSource[self.comboBox_trigger_source.currentText()],
        )

        return detector_settings

    def apply_detector_settings(self):

        logging.info(f"Applying detector settings")
        self.microscope._detector.settings = self.get_detector_settings_from_ui()

        # TODO: actually apply these settings to the detector

        napari.utils.notifications.show_info(
            f"Applied detector settings: {self.microscope._detector.settings}"
        )

    ### Laser Controller
    def apply_laser_settings(self):

        laser_settings = self.get_laser_settings_from_ui()
        logging.info(f"Laser: {laser_settings}")

        lc_settings = self.get_laser_controller_settings_from_ui()
        logging.info(f"Laser Controller: {lc_settings}")
        
        # get current laser
        current_laser = self.comboBox_selected_laser.currentText()
        laser_controller = self.microscope.get_laser_controller()

        # update settings
        laser_controller.lasers[current_laser].set(laser_settings)

        if laser_settings.power > 5.0:
            napari.utils.notifications.show_warning(f"Laser power is set to {laser_settings.power}%. Please check the laser settings.")
        else:
            napari.utils.notifications.show_info(
                f"Settings applied to Laser: {current_laser}"
            )

    def get_laser_settings_from_ui(self):

        laser_settings = LaserSettings(
            name=self.lineEdit_laser_name.text(),
            serial_id=self.lineEdit_laser_id.text(),
            wavelength=int(self.spinBox_laser_wavelength.value()),
            power=self.doubleSpinBox_laser_power.value(),
            exposure_time=self.doubleSpinBox_laser_exposure.value() * constants.MILLI_TO_SI,
            enabled=self.checkBox_laser_enabled.isChecked(),
            colour=str(self.label_laser_color.text()).split(","),
        )
        logging.info(f"Laser settings: {laser_settings}")
        return laser_settings


    def get_laser_controller_settings_from_ui(self):

        lc_settings = LaserControllerSettings(
            name=self.lineEdit_lc_name.text(),
            connection=self.microscope.get_laser_controller().settings.connection,
            laser=self.lineEdit_lc_type.text(),
        )
        return lc_settings
        
    
    def set_ui_from_laser_settings(self, laser_settings: LaserSettings):

        self.lineEdit_laser_name.setText(laser_settings.name)
        self.lineEdit_laser_id.setText(laser_settings.serial_id)
        self.spinBox_laser_wavelength.setValue(int(laser_settings.wavelength))
        self.doubleSpinBox_laser_power.setValue(laser_settings.power)
        self.doubleSpinBox_laser_exposure.setValue(laser_settings.exposure_time * constants.SI_TO_MILLI)

        self.checkBox_laser_enabled.setChecked(laser_settings.enabled)
        self.label_laser_color.setText(str(laser_settings.colour))


    def set_ui_from_laser_controller_settings(self, lc_settings: LaserControllerSettings):
        self.lineEdit_lc_name.setText(lc_settings.name)
        self.lineEdit_lc_type.setText(lc_settings.laser)

    ### Objective
    def get_position(self):

        logging.info(f"Position: {self.microscope._objective.position:.2e}")

        self.update_ui()

        return self.microscope._objective.position

    def save_position(self):
       
        self.microscope._objective.save_position(self.microscope._objective.position)
        logging.info(f"Saved position: {self.microscope._objective.saved_position:.2e}")
        self.update_ui()

    def move_absolute(self):

        abs_position = (
            self.doubleSpinBox_absolute_position.value() * constants.MICRO_TO_SI
        )
        logging.info(f"Absolute position: {abs_position:.2e}")

        self.microscope._objective.absolute_move(abs_position)
        self.update_ui()

    def move_relative(self):

        relative_position = (
            self.doubleSpinBox_relative_position.value() * constants.MICRO_TO_SI
        )

        if self.sender() == self.pushButton_move_relative_up:
            direction = "up"
        if self.sender() == self.pushButton_move_relative_down:
            direction = "down"
            relative_position *= -1

        logging.info(f"Relative position: {relative_position:.2e}, ({direction})")

        self.microscope._objective.relative_move(relative_position)

        self.update_ui()

    def set_ui_from_objective(self, objective: ObjectiveStage):
        import time
        time.sleep(0.2)
        self.doubleSpinBox_current_position.setValue(
            objective.position * constants.SI_TO_MICRO
        )

        if objective.saved_position is not None:
            self.doubleSpinBox_saved_position.setValue(
                objective.saved_position * constants.SI_TO_MICRO
            )














def main():

    from openclem import utils
    from openclem.microscopes.base import BaseLightMicroscope

    lc, det, obj = utils.setup_session()

    lm: BaseLightMicroscope = utils.create_microscope("test", det, lc, obj)

    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMHardwareWidget(viewer=viewer, microscope=lm)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

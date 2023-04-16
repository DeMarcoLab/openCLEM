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
                                 TriggerEdge, TriggerSource)
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

        # laser ui
        self.setup_laser_ui()
    
        # objective
        self.pushButton_get_position.clicked.connect(self.get_position)
        self.pushButton_save_position.clicked.connect(self.save_position)
        self.pushButton_goto_saved_position.clicked.connect(self.goto_saved_position)
        self.pushButton_move_absolute.clicked.connect(self.move_absolute)
        self.pushButton_move_relative_down.clicked.connect(self.move_relative)
        self.pushButton_move_relative_up.clicked.connect(self.move_relative)

        # dont allow editing
        self.doubleSpinBox_current_position.setEnabled(False)
        self.doubleSpinBox_saved_position.setEnabled(False)

    def setup_laser_ui(self):
        self.laser_ui = []

        laser: Laser
        for laser in self.microscope._laser_controller.lasers.values():
            label = QtWidgets.QLabel(laser.name)
            spinBox_power = QtWidgets.QDoubleSpinBox()
            spinBox_exposure = QtWidgets.QDoubleSpinBox()
            # no decimals
            spinBox_power.setDecimals(0)
            spinBox_exposure.setDecimals(0)
            # set range
            spinBox_power.setRange(0, 100)
            spinBox_exposure.setRange(0, 10000)

            checkBox_enable = QtWidgets.QCheckBox()

            info = {} # container for name, serial_id, wavelength and color
            self.laser_ui.append([label, spinBox_power, spinBox_exposure, checkBox_enable, info])
            r = self.gridLayout_laser.rowCount()
            self.gridLayout_laser.addWidget(label, r, 0)
            self.gridLayout_laser.addWidget(spinBox_power, r, 1)
            self.gridLayout_laser.addWidget(spinBox_exposure, r, 2)
            self.gridLayout_laser.addWidget(checkBox_enable, r, 3)


    def update_ui(self):
        self.set_ui_from_detector_settings(self.microscope._detector.settings)
        self.set_ui_from_objective(self.microscope._objective)

        self.set_ui_from_laser_controller_settings(self.microscope._laser_controller.settings)
        self.set_laser_ui()


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
        self.microscope._detector.settings = self.get_detector_settings_from_ui()

        # TODO: actually apply these settings to the detector

        napari.utils.notifications.show_info(
            f"Applied detector settings: {self.microscope._detector.settings}"
        )

    ### Laser Controller
    # TODO: fix laser info, looks ugly
    # TODO: set width of ui properly on startup?
    # TODO: be smarter about how we update the ui, dont necessarily need to redraw everything, and update all lasers
    def get_laser_settings_from_ui(self, idx: int):

        laser = self.laser_ui[idx]

        # info = laser[0].text()
        # name = info.split(" - ")[0].strip()
        # serial_id = str(info.split(" - ")[1].strip()[1:-1])
        # color = info.split(" - ")[2].strip()
        # color = list(map(float, color[1:-1].split(",")))

        # extra info (not shown to user)
        info = laser[4]
        name = info["name"]
        serial_id = info["serial_id"]
        color = info["color"]
        wavelength = info["wavelength"]

        return LaserSettings(
            name = name,
            serial_id=serial_id, 
            wavelength = wavelength,
            power = laser[1].value(),
            exposure_time = laser[2].value() * constants.MILLI_TO_SI,
            enabled = laser[3].isChecked(),
            color=color,
        )
    
    def set_laser_ui(self):
        # loop through all lasers, and update the relevant UI elements
        laser: Laser
        for i, laser in enumerate(self.microscope._laser_controller.lasers.values()):
            
            settings: LaserSettings = laser.get()
            self.set_ui_from_laser_settings(settings, i)

    def set_ui_from_laser_settings(self, settings: LaserSettings, idx: int) -> None:
        
        info = f"Channel {int(settings.wavelength)}nm"
        self.laser_ui[idx][0].setText(info)
        self.laser_ui[idx][1].setValue(settings.power)
        self.laser_ui[idx][2].setValue(settings.exposure_time * constants.SI_TO_MILLI)
        self.laser_ui[idx][3].setChecked(settings.enabled)
        self.laser_ui[idx][4] = {
            "name": settings.name,
            "serial_id": settings.serial_id,
            "wavelength": settings.wavelength,
            "color": settings.color,
        }

    def apply_laser_settings(self):

        laser: Laser
        for idx, laser in enumerate(self.microscope._laser_controller.lasers.values()):
            settings = self.get_laser_settings_from_ui(idx)
            logging.info(f"Laser {idx}: {settings}")

            laser.apply_settings(settings)
        
        napari.utils.notifications.show_info(f"Applied laser settings.")


    def set_ui_from_laser_controller_settings(self, lc_settings: LaserControllerSettings):
        self.label_lc_name.setText(f"Laser Controller: {lc_settings.name}, Lasers: {lc_settings.laser}")

    ### Objective
    def get_position(self):

        logging.info(f"Position: {self.microscope._objective.position:.2e}")

        self.update_ui()

        return self.microscope._objective.position

    def save_position(self):

        self.microscope._objective.save_position(self.microscope._objective.position)
        logging.info(f"Saved position: {self.microscope._objective.saved_position:.2e}")
        self.update_ui()

    def goto_saved_position(self):

        position = self.microscope._objective.saved_position
        logging.info(f"Moving to saved position: {position:.2e}")
        self.microscope._objective.absolute_move(position)
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

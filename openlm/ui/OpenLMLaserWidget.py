
import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openlm import constants, utils
from openlm.detector import Detector
from openlm.laser import Laser, LaserController
from openlm.structures import (ImageSettings, LaserControllerSettings, LaserSettings)
from openlm.ui.qt import OpenLMLaserWidget


class OpenLMLaserWidget(OpenLMLaserWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        lc: LaserController,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(OpenLMLaserWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.lc = lc

        self.setup_connections()

        self.update_ui()


    def setup_connections(self):
        print("setup_connections")

        self.pushButton_apply_laser_settings.clicked.connect(
            self.apply_laser_settings
        )

        self.comboBox_selected_laser.addItems(self.lc.lasers.keys())
        self.comboBox_selected_laser.currentTextChanged.connect(self.update_ui)

    def update_ui(self):
        print("update_ui")
        self.set_laser_controller_settings_from_ui(self.lc.settings)
        current_laser = self.comboBox_selected_laser.currentText()
        self.set_laser_settings_from_ui(self.lc.lasers[current_laser].settings)

    def apply_laser_settings(self):
        print("apply_laser_settings")

        laser_settings = self.get_laser_settings_from_ui()
        # self.lc.set_laser_settings(laser_settings)
        print(laser_settings)

        lc_settings = self.get_laser_controller_settings_from_ui()
        print(lc_settings)

        napari.utils.notifications.show_info(
            f"Settings applied to {self.lc.settings.name}"
            )

    def get_laser_settings_from_ui(self):

        print("get_laser_settings_from_ui")

        laser_settings = LaserSettings(
            name=self.lineEdit_laser_name.text(),
            serial_id=self.lineEdit_laser_id.text(),
            wavelength=int(self.spinBox_laser_wavelength.value()),
            power=self.doubleSpinBox_laser_power.value(),
            exposure_time=self.doubleSpinBox_laser_exposure.value() * constants.MILLI_TO_SI,
            enabled=self.checkBox_laser_enabled.isChecked(),
            color=str(self.label_laser_color.text()).split(","),
        )

        return laser_settings


    def get_laser_controller_settings_from_ui(self):

            print("get_laser_controller_settings_from_ui")

            lc_settings = LaserControllerSettings(
                name=self.lineEdit_lc_name.text(),
                connection=None,
                laser=self.lineEdit_lc_type.text(),
            )

            return lc_settings


    def set_laser_settings_from_ui(self, laser_settings: LaserSettings):
        print("set_laser_settings_from_ui")

        self.lineEdit_laser_name.setText(laser_settings.name)
        self.lineEdit_laser_id.setText(laser_settings.serial_id)
        self.spinBox_laser_wavelength.setValue(int(laser_settings.wavelength))
        self.doubleSpinBox_laser_power.setValue(laser_settings.power)
        self.doubleSpinBox_laser_exposure.setValue(laser_settings.exposure_time * constants.SI_TO_MILLI)

        self.checkBox_laser_enabled.setChecked(laser_settings.enabled)
        self.label_laser_color.setText(str(laser_settings.color))

    def set_laser_controller_settings_from_ui(self, lc_settings: LaserControllerSettings):
        print("set_laser_controller_settings_from_ui")

        self.lineEdit_lc_name.setText(lc_settings.name)
        self.lineEdit_lc_type.setText(lc_settings.laser)

def main():
    lc, detector = utils.setup_session()

    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = OpenLMLaserWidget(viewer=viewer, lc=lc)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

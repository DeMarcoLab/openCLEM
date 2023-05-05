import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

logging.basicConfig(level=logging.INFO)

import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openlm import constants, utils
from openlm.detector import Detector
from openlm.laser import Laser, LaserController
from openlm.microscope import LightMicroscope
from openlm.objective import ObjectiveStage
from openlm.structures import (DetectorSettings, ExposureMode, ImageSettings,
                                 LaserControllerSettings, LaserSettings,
                                 TriggerEdge, TriggerSource)
from openlm.ui.qt import OpenLMHardwareWidget, OpenLMObjectiveWidget

from openlm.ui.qt import OpenLMCalibrationWidget


try:
    from fibsem import constants, conversions
    from fibsem.structures import BeamType, Point, FibsemStagePosition
    FIBSEM = True
except ImportError:
    FIBSEM = False


class OpenLMCalibrationWidget(OpenLMCalibrationWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        microscope: LightMicroscope = None, 
        parent=None,
    ):
        super(OpenLMCalibrationWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.parent = parent
        self.viewer = viewer
        self.microscope = microscope
        self.setup_connections()

        self.reset_calibration()

        self.update_ui()

    def setup_connections(self):
        logging.info("setup_connections")

        self.pushButton_move_stage.clicked.connect(self.move_stage)
        self.pushButton_calculate_pretilt.clicked.connect(self.calculate_pretilt)
        self.pushButton_save_calibration.clicked.connect(self.save_calibration)
        self.pushButton_reset_calibration.clicked.connect(self.reset_calibration)

        # self.pushButton_calculate_pretilt.setVisible(False)


    def update_ui(self):
        self.label_pretilt.setText(f"{self.microscope.fibsem_settings.system.stage.tilt_flat_to_electron:.2f} deg")
        self.label_objective_start.setText(f"Objective Start: {(self.obj_z0 * constants.SI_TO_MICRO):.2f} um")
        self.label_objective_finish.setText(f"Objective dz: {(self.obj_dz * constants.SI_TO_MICRO):.2f} um")
        self.label_cum_dy.setText(f"{(self._cum_dy * constants.SI_TO_MICRO):.2f} um")
        self.label_cum_dy_corrected.setText(f"{(self._cum_dy_corrected * constants.SI_TO_MICRO):.2f} um")
        self.label_cum_dz_corrected.setText(f"{(self._cum_dz_corrected * constants.SI_TO_MICRO):.2f} um")
        self.label_dpretilt.setText(f"{self.dpretilt:.4f} deg")



    def reset_calibration(self):

        logging.info("reset_calibration")

        self._cum_dy = 0.0
        self._cum_dy_corrected = 0.0
        self._cum_dz_corrected = 0.0
        self.dpretilt = 0.0 

        self.obj_z0 = self.microscope._objective.position
        self.obj_z1 = self.obj_z0
        self.obj_dz = self.obj_z1 - self.obj_z0

        self.update_ui()


    def move_stage(self):
        logging.info("move_stage")


        if self.microscope.fibsem_microscope is None:
            msg = f"Stage Movement is disabled (No OpenFIBSEM)"
            napari.utils.notifications.show_info(msg)
            logging.info(msg)
            return

        dy = self.doubleSpinBox_dy.value() * constants.MICRO_TO_SI

        logging.info(f"Moving stage by {dy} um")

        stage_position = self.microscope.fibsem_microscope.stable_move(
            settings=self.microscope.fibsem_settings,
            dx=0,
            dy=dy,
            beam_type=BeamType.ION,
        )
        
        self._cum_dy += dy
        self._cum_dy_corrected += stage_position.y
        self._cum_dz_corrected += stage_position.z

        self.calculate_pretilt()

        self.update_ui()


    def calculate_pretilt(self):
        logging.info("calculate_pretilt")

        self.obj_z1 = self.microscope._objective.position
        # change in dz is the change in z of the objective
        # divided by cum_dy
        # pretilt is the arctan of that

        self.obj_dz = -(self.obj_z1 - self.obj_z0) # sign is  because coord sysstems are opposite

        self.dpretilt = np.rad2deg(np.arctan(self.obj_dz / self._cum_dy))

        self.update_ui()

        # TODO: hook up to objective stage movement

    def save_calibration(self):
        logging.info("save_calibration")


        # save the pretilt
        # self.microscope.fibsem_settings.system.stage.tilt_flat_to_electron += self.dpretilt
        self.parent.microscope.fibsem_settings.system.stage.tilt_flat_to_electron += self.dpretilt

        # TODO: need to update the parent


        # save to file
        # allow raw editing of value

        self.update_ui()


def main():

    # create the viewer and window
    viewer = napari.Viewer(ndisplay=2)
    
    openlm_calibration = OpenLMCalibrationWidget(viewer=viewer)

    viewer.window.add_dock_widget(
        openlm_calibration, area="right", add_vertical_stretch=False, name="OpenLM Calibration"
    )
    napari.run()


if __name__ == "__main__":
    main()

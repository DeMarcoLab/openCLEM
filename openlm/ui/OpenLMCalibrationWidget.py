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

from openlm import constants
from openlm.microscope import LightMicroscope
from openlm.ui.qt import OpenLMCalibrationWidget

try:
    from fibsem import constants, conversions
    from fibsem.structures import BeamType, FibsemStagePosition, Point

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

        self.pushButton_calculate_pretilt.setVisible(False)

        if self.parent is not None:
            self.parent.hardware_widget.objective_moved.connect(self.calculate_pretilt)

        self.pushButton_move_stage_flat.clicked.connect(self.move_flat_to_beam)

    def update_ui(self):
        stage_msg = (
            f"Stage:\nExpected (dy): \t{(self._cum_dy * constants.SI_TO_MICRO):.2f} um"
        )
        stage_msg += (
            f"\nActual (dy): \t{(self._cum_dy_corrected * constants.SI_TO_MICRO):.2f} um"
        )
        stage_msg += (
            f"\nActual (dz): \t{(self._cum_dz_corrected * constants.SI_TO_MICRO):.2f} um"
        )

        obj_msg = (
            f"\nObjective:\nStart (z): \t{(self.obj_z0 * constants.SI_TO_MICRO):.2f} um"
        )
        obj_msg += f"\nDelta (dz): \t{(self.obj_dz * constants.SI_TO_MICRO):.2f} um"

        pretilt_msg = f"\nPre-Tilt:\nStart: \t\t{self.microscope.fibsem_settings.system.stage.pre_tilt:.2f} deg"
        pretilt_msg += f"\nDelta: \t\t{self.dpretilt:.4f} deg"

        instruction_msg = f"Instructions:"
        instruction_msg += f"\n1. Move stage to a position where the sample is in focus, and press Reset Calibration"
        instruction_msg += f"\n2. Move stage in steps of {self.doubleSpinBox_dy.value()} um until the sample is out of focus"
        instruction_msg += f"\n3. Refocus using the Objective (Hardware Tab)'"
        instruction_msg += f"\n4. Click 'Save Calibration' to update the pre-tilt angle"
        instruction_msg += f"\n5. Click 'Reset Calibration' to start over"
        instruction_msg += f"\n\nYou should now be able to click to move along the sample without refocusing.\n\n"

        msg = f"{stage_msg}\n{obj_msg}\n{pretilt_msg}\n\n{instruction_msg}"

        self.label_info.setText(msg)

        # flat to beam
        flat_to_ion = self.microscope.fibsem_settings.system.stage.tilt_flat_to_ion
        pre_tilt = self.microscope.fibsem_settings.system.stage.pre_tilt
        target = flat_to_ion - pre_tilt
        msg = f"Flat to Beam: {target:.2f} deg (Ion Tilt: {flat_to_ion:.2f} deg, Pre-Tilt: {pre_tilt:.2f} deg)"
        self.label_move_stage_flat.setText(msg)

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

        self.obj_dz = -(
            self.obj_z1 - self.obj_z0
        )  # sign is  because coord sysstems are opposite

        if np.isclose(self.obj_dz, 0.0) or np.isclose(self._cum_dy, 0.0):
            return

        self.dpretilt = np.rad2deg(np.arctan(self.obj_dz / (self._cum_dy+1e-20)))

        self.update_ui()

    def save_calibration(self):
        logging.info("save_calibration")

        # save the pretilt
        self.parent.microscope.fibsem_settings.system.stage.pre_tilt += self.dpretilt

        self.update_ui()

    def move_flat_to_beam(self):

        self.microscope.fibsem_microscope.move_flat_to_beam(settings=self.microscope.fibsem_settings, 
                                                            beam_type=BeamType.ION)

# TODO:
# - give access to system pre-tilt through UI
# - write changes to system.yaml
# - safety checks


def main():
    # create the viewer and window
    viewer = napari.Viewer(ndisplay=2)

    openlm_calibration = OpenLMCalibrationWidget(viewer=viewer)

    viewer.window.add_dock_widget(
        openlm_calibration,
        area="right",
        add_vertical_stretch=False,
        name="OpenLM Calibration",
    )
    napari.run()


if __name__ == "__main__":
    main()

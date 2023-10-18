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

from openlm.ui.qt import OpenLMPositionWidget

try:
    from fibsem import constants, conversions
    from fibsem import utils as fibsem_utils
    from fibsem.microscope import FibsemMicroscope
    from fibsem.structures import (
        BeamType,
        FibsemStagePosition,
        MicroscopeSettings,
        Point,
        MicroscopeState
    )

    FIBSEM = True
except ImportError:
    FIBSEM = False


from copy import deepcopy

from openlm import config as cfg
from openlm import utils
from openlm.structures import Experiment


_DESTINATION = {"LM": "FIBSEM", "FIBSEM": "LM", "Unknown": "Unknown"}


class OpenLMPositionWidget(OpenLMPositionWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        microscope: FibsemMicroscope,
        settings: MicroscopeSettings,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(OpenLMPositionWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.parent = parent
        self.viewer = viewer
        self.microscope = microscope
        self.settings = settings
        self._translation = cfg._TRANSLATION

        EXP_NAME = f"piedisc_{utils.current_timestamp()}"
        self.experiment = Experiment(cfg.LOG_PATH, name=EXP_NAME)
        self.experiment.translation = self._translation

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        logging.info("setup_connections")

        self.pushButton_add_coordinate.clicked.connect(self.add_coordinate)
        self.pushButton_add_coordinate.setStyleSheet("background-color: green")
        self.pushButton_remove_coordinate.clicked.connect(self.remove_coordinate)
        self.pushButton_remove_coordinate.setStyleSheet("background-color: red")
        self.pushButton_save_coordinate.clicked.connect(self.save_coordinates)
        self.pushButton_save_coordinate.setStyleSheet("background-color: blue")

        self.comboBox_move_to_system.addItems(["Light Microscope", "FIBSEM"])
        self.pushButton_move_to_position.clicked.connect(self.move_to_position)

        self.doubleSpinBox_translation_x.setValue(
            self._translation["x"] * constants.SI_TO_MILLI
        )
        self.doubleSpinBox_translation_y.setValue(
            self._translation["y"] * constants.SI_TO_MILLI
        )
        self.doubleSpinBox_translation_z.setValue(
            self._translation["z"] * constants.SI_TO_MILLI
        )
        self.doubleSpinBox_translation_x.valueChanged.connect(self._update_translation)
        self.doubleSpinBox_translation_y.valueChanged.connect(self._update_translation)
        self.doubleSpinBox_translation_z.valueChanged.connect(self._update_translation)
        self.doubleSpinBox_translation_x.setKeyboardTracking(False)
        self.doubleSpinBox_translation_y.setKeyboardTracking(False)
        self.doubleSpinBox_translation_z.setKeyboardTracking(False)

        self.pushButton_move_to_microscope.clicked.connect(self._move_to_microscope)

    def update_ui(self):
        logging.info("update_ui")

        self.comboBox_positions.clear()
        self.comboBox_positions.addItems(
            [f"Position {i+1:02d}" for i in range(len(self.experiment.positions))]
        )

        msg = "Saved Positions: \n"
        msg += "LM Position \t\t\t\t FIBSEM Position \n"
        pos: list[tuple[MicroscopeState, MicroscopeState]]
        for pos in self.experiment.positions:

            lm_pos = pos[0].absolute_position  # assume in LM coordinates
            fibsem_pos = pos[1].absolute_position  # assume in LM coordinates

            # fibsem_pos = deepcopy(pos)
            # _translation = _get_req_translation(self._update_translation(), "LM")
            # fibsem_pos.x += _translation["x"]
            # fibsem_pos.y += _translation["y"]
            # fibsem_pos.z += _translation["z"]

            msg += f"{lm_pos._scale_repr(constants.SI_TO_MILLI)}"
            msg += "\t\t\t"
            msg += f"{fibsem_pos._scale_repr(constants.SI_TO_MILLI)}\n"

        self.label_coordinate_list.setText(msg)

        # current position
        pos = self.microscope.get_stage_position()
        _cur_mic = self._get_current_microscope()
        msg = f"Current Position: {pos._scale_repr(constants.SI_TO_MILLI)} ({_cur_mic})"
        self.label_microscope_position.setText(msg)

        # update button text
        _dest_mic = _DESTINATION[_cur_mic]
        msg = f"Move from {_cur_mic} to {_dest_mic}"
        self.pushButton_move_to_microscope.setText(msg)

    def add_coordinate(self):
        logging.info("add_coordinate")

        # get the current stage position
        state = self.microscope.get_current_microscope_state()

        _current_microscope = self._get_current_microscope()

        if _current_microscope not in ["FIBSEM", "LM"]:
            logging.warning(f"Unknown microscope: {_current_microscope}")
            return

        _translation = _get_req_translation(self._update_translation(), _current_microscope)

        other = deepcopy(state)
        other.absolute_position.x += _translation["x"]
        other.absolute_position.y += _translation["y"]
        other.absolute_position.z += _translation["z"]

        # if the microscope is in FIBSEM coordinates, convert to LM coordinates
        if _current_microscope == "LM":
            dat = [state, other]
        if _current_microscope == "FIBSEM":
            dat = [other, state]

        # add the positions to the lists
        self.experiment.positions.append(deepcopy(dat))

        self.update_ui()

    def remove_coordinate(self):
        logging.info("remove_coordinate")

        # remove the last stage position from the list
        if self.experiment.positions:
            idx = self.comboBox_positions.currentIndex()
            self.experiment.positions.pop(idx)

        self.update_ui()

    def save_coordinates(self):
        logging.info("save_coordinates")

        from pprint import pprint

        # print the list of stage positions
        pprint(self.experiment.positions)

        print(f"Saving coordinates to {self.experiment.path}")
        self.experiment.save()

        self.update_ui()

    def move_to_position(self):
        # TODO: redo this
        if not self.experiment.positions:
            logging.warning("No positions saved")
            return

        idx = self.comboBox_positions.currentIndex()
        coord_system = self.comboBox_move_to_system.currentText()

        if coord_system == "Light Microscope":
            coord = 0
        elif coord_system == "FIBSEM":
            coord = 1

        pos = deepcopy(
            self.experiment.positions[idx][coord].absolute_position
        )  
        
        # if coord_system == "FIBSEM":        
        #     # _start = "LM"
        #     # _translation = _get_req_translation(self._update_translation(), _start)
        #     # pos.x += _translation["x"]
        #     # pos.y += _translation["y"]
        #     # pos.z += _translation["z"]
        # else:
        #     _start = "FIBSEM"
        #     pass

        print(f"Moving to {coord_system} position: {pos}")
        self.microscope.move_stage_absolute(pos)

        self.update_ui()

    def _update_translation(self):
        self._translation["x"] = (
            self.doubleSpinBox_translation_x.value() * constants.MILLI_TO_SI
        )
        self._translation["y"] = (
            self.doubleSpinBox_translation_y.value() * constants.MILLI_TO_SI
        )
        self._translation["z"] = (
            self.doubleSpinBox_translation_z.value() * constants.MILLI_TO_SI
        )

        return deepcopy(self._translation)

    def _get_current_microscope(self):
        pos = self.microscope.get_stage_position()
        current_position_x = pos.x
        fibsem_min = -10.0e-3
        fibsem_max = 10.0e-3
        lm_min = 40.0e-3
        lm_max = 60.0e-3

        msg: str
        if fibsem_min < current_position_x < fibsem_max:
            msg = f"FIBSEM"
        elif lm_min < current_position_x < lm_max:
            msg = f"LM"
        else:
            msg = f"Unknown"
        return msg

    def _move_to_microscope(self):
        _translation = self._update_translation()
        _start_microscope = self._get_current_microscope()
        _translation = _get_req_translation(_translation, _start_microscope)

        # move to microscope
        _dest_microscope = _DESTINATION[_start_microscope]
        msg = f"Moving to {_start_microscope} -> {_dest_microscope}"
        logging.info(msg)
        napari.utils.notifications.show_info(msg)

        x, y, z = _translation["x"], _translation["y"], _translation["z"]
        logging.info(f"Moving relative to {_dest_microscope}: x={x}, y={y}, z={z}")
        new_position = FibsemStagePosition(x=x, y=y, z=z, r=0, t=0)
        self.microscope.move_stage_relative(new_position)

        self.update_ui()

def _get_req_translation(translation: dict, _start: str) -> dict:
    if _start not in ["FIBSEM", "LM"]:
        logging.warning("Unknown")
        translation = None
    # move to FIBSEM
    if _start == "LM":
        # invert translation
        translation["x"] *= -1
        translation["y"] *= -1
        translation["z"] *= -1

    return translation


# save the coordinates to a file
# save the shift between microscopes
# import to autolamella + ref_image + lamella_coordinates


# TODO:
# check if position is lm or fibsem
# probably lock it to only one microscope
# check if shift is correct or absolute moves make it different


def main():
    # create the viewer and window
    viewer = napari.Viewer(ndisplay=2)

    microscope, settings = fibsem_utils.setup_session(
        manufacturer="Thermo", ip_address="10.0.0.1"
    )
    openlm_coordinate = OpenLMPositionWidget(
        microscope=microscope, settings=settings, viewer=viewer
    )

    viewer.window.add_dock_widget(
        openlm_coordinate,
        area="right",
        add_vertical_stretch=False,
        name="OpenLM Coordinate Widget",
    )
    napari.run()


if __name__ == "__main__":
    main()

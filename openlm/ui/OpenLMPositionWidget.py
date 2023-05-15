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
    from fibsem.structures import (BeamType, FibsemStagePosition,
                                   MicroscopeSettings, Point)
    FIBSEM = True
except ImportError:
    FIBSEM = False


from copy import deepcopy

from openlm import config as cfg
from openlm import utils
from openlm.structures import Experiment


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

        # self.positions = []

        EXP_NAME = f"piedisc_{utils.current_timestamp()}"
        self.experiment = Experiment(cfg.LOG_PATH, name=EXP_NAME)
        self.experiment.translation = cfg._TRANSLATION

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

    def update_ui(self):
        logging.info("update_ui")

        self.comboBox_positions.clear()
        self.comboBox_positions.addItems([f"Position {i+1:02d}" for i in range(len(self.experiment.positions))])

        msg = "Saved Positions: \n"
        msg += "LM Position \t\t\t\t FIBSEM Position \n"
        for state in self.experiment.positions:
            pos = state.absolute_position # assume in LM coordinates

            fibsem_pos = deepcopy(pos)
            fibsem_pos.x -= cfg._TRANSLATION["x"]
            fibsem_pos.y -= cfg._TRANSLATION["y"]
            fibsem_pos.z -= cfg._TRANSLATION["z"]
            msg += f"{pos._scale_repr(constants.SI_TO_MILLI)}"
            msg += "\t\t\t"
            msg += f"{fibsem_pos._scale_repr(constants.SI_TO_MILLI)}\n"

        msg += f"\n\nCurrent Position: {self._get_current_position()}"

        self.label_coordinate_list.setText(msg)

    def add_coordinate(self):
        logging.info("add_coordinate")

        # get the current stage position
        state = self.microscope.get_current_microscope_state()

        # add the stage position to the list
        self.experiment.positions.append(deepcopy(state))

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

        if not self.experiment.positions:
            logging.warning("No positions saved")
            return

        idx = self.comboBox_positions.currentIndex()
        coord_system = self.comboBox_move_to_system.currentText()

        pos = deepcopy(self.experiment.positions[idx].absolute_position) # assume in LM coordinates
        if not (coord_system == "Light Microscope"):
            pos.x -= cfg._TRANSLATION["x"]
            pos.y -= cfg._TRANSLATION["y"]
            pos.z -= cfg._TRANSLATION["z"]

            coord_system = "FIBSEM"

        print(f"Moving to {coord_system} position: {pos}")
        self.microscope.move_stage_absolute(pos)

        self.update_ui()


    def _get_current_position(self):

        _translation = cfg._TRANSLATION

        pos  = self.microscope.get_stage_position()
        current_position_x = pos.x
        fibsem_min = -10.0e-3
        fibsem_max = 10.0e-3
        lm_min = 40.0e-3
        lm_max = 60.0e-3

        # x = _translation["x"]
        # y = _translation["y"]
        # z = _translation["z"]

        msg: str
        if fibsem_min < current_position_x < fibsem_max:
            msg = f"FIBSEM"
        elif lm_min < current_position_x < lm_max:
            # x = -x
            # y = -y
            # z = -z
            msg = f"LM"
        else:
            msg = f"Not under either microscope: " 
        return f"{pos._scale_repr(constants.SI_TO_MILLI)} ({msg})"
    
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
    

    microscope, settings = fibsem_utils.setup_session(manufacturer="Thermo", ip_address="10.0.0.1")
    openlm_coordinate = OpenLMPositionWidget(microscope=microscope, settings=settings, viewer=viewer)

    viewer.window.add_dock_widget(
        openlm_coordinate, area="right", add_vertical_stretch=False, name="OpenLM Coordinate Widget"
    )
    napari.run()


if __name__ == "__main__":
    main()

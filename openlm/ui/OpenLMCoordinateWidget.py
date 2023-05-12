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
from openlm.ui.qt import OpenLMCoordinateWidget


try:
    from fibsem.microscope import FibsemMicroscope
    from fibsem import constants, conversions
    from fibsem import utils as fibsem_utils 
    from fibsem.structures import BeamType, Point, FibsemStagePosition, MicroscopeSettings
    FIBSEM = True
except ImportError:
    FIBSEM = False


from openlm.structures import Experiment
from openlm import config as cfg
from openlm import utils    

from copy import deepcopy



class OpenLMCoordinateWidget(OpenLMCoordinateWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        microscope: FibsemMicroscope, 
        settings: MicroscopeSettings,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(OpenLMCoordinateWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.parent = parent
        self.viewer = viewer
        self.microscope = microscope
        self.settings = settings

        # self.positions = []

        EXP_NAME = f"piedisc_{utils.current_timestamp()}"
        self.experiment = Experiment(cfg.LOG_PATH, name=EXP_NAME)

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
        self.comboBox_positions.addItems([f"Position {i:02d}" for i in range(len(self.experiment.positions))])

        msg = "Saved Positions: \n"
        msg += "LM Position \t\t\t\t FIBSEM Position \n"
        for state in self.experiment.positions:
            pos = state.absolute_position # assume in LM coordinates

            fibsem_pos = deepcopy(pos)
            fibsem_pos.x -= cfg._TRANSLATION["x"]
            fibsem_pos.y -= cfg._TRANSLATION["y"]
            fibsem_pos.z -= cfg._TRANSLATION["z"]
            msg += f"x:{pos.x*constants.SI_TO_MILLI:.2f} y:{pos.y*constants.SI_TO_MILLI:.2f} z:{pos.z*constants.SI_TO_MILLI:.2f}"
            msg += "\t\t"
            msg += f"x:{fibsem_pos.x*constants.SI_TO_MILLI:.2f} y:{fibsem_pos.y*constants.SI_TO_MILLI:.2f} z:{fibsem_pos.z*constants.SI_TO_MILLI:.2f}\n"

        self.label_coordinate_list.setText(msg)

    def add_coordinate(self):
        logging.info("add_coordinate")

        # get the current stage position
        state = deepcopy(self.microscope.get_current_microscope_state())

        # add the stage position to the list
        self.experiment.positions.append(state)

        self.update_ui()
    

    def remove_coordinate(self):
        logging.info("remove_coordinate")

        # remove the last stage position from the list
        if self.experiment.positions:
            self.experiment.positions.pop()

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

        idx = self.comboBox_positions.currentIndex()
        coord_system = self.comboBox_move_to_system.currentText()

        pos = self.experiment.positions[idx].absolute_position # assume in LM coordinates
        if not (coord_system == "Light Microscope"):
            pos.x -= cfg._TRANSLATION["x"]
            pos.y -= cfg._TRANSLATION["y"]
            pos.z -= cfg._TRANSLATION["z"]

            coord_system = "FIBSEM"

        print(f"Moving to {coord_system} position: {pos}")
        self.microscope.move_stage_absolute(pos)

    
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
    openlm_coordinate = OpenLMCoordinateWidget(microscope=microscope, settings=settings, viewer=viewer)

    viewer.window.add_dock_widget(
        openlm_coordinate, area="right", add_vertical_stretch=False, name="OpenLM Coordinate Widget"
    )
    napari.run()


if __name__ == "__main__":
    main()

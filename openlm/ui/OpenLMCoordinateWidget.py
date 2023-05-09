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

        self.positions = []

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        logging.info("setup_connections")


        self.pushButton_add_coordinate.clicked.connect(self.add_coordinate)
        self.pushButton_remove_coordinate.clicked.connect(self.remove_coordinate)
        self.pushButton_save_coordinate.clicked.connect(self.save_coordinates)


    def update_ui(self):
        logging.info("update_ui")

        msg = "Saved Positions: \n"
        for pos in self.positions:
            msg += f"x:{pos.x*constants.SI_TO_MILLI:.2f} y:{pos.y*constants.SI_TO_MILLI:.2f} z:{pos.z*constants.SI_TO_MILLI:.2f} \n"

        self.label_coordinate_list.setText(msg)



    def add_coordinate(self):
        logging.info("add_coordinate")

        import random 
        # dx = random.randint(0, 100) * 1e-6
        # dy = random.randint(0, 100) * 1e-6
        # move stge by random amount
        # self.microscope.stable_move(self.settings, dx=dx, dy=dy, beam_type=BeamType.ELECTRON)

        # get the current stage position
        from copy import deepcopy
        stage_position = deepcopy(self.microscope.get_stage_position())

        # add the stage position to the list
        self.positions.append(stage_position)

        self.update_ui()
    

    def remove_coordinate(self):
        logging.info("remove_coordinate")

        # remove the last stage position from the list
        if self.positions:
            self.positions.pop()

        self.update_ui()


    def save_coordinates(self):
        logging.info("save_coordinates")
    
        from pprint import pprint

        # print the list of stage positions
        pprint(self.positions)    

        self.update_ui()




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

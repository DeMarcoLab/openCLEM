import os
from copy import deepcopy
from pathlib import Path

import napari
import napari.utils.notifications
import numpy as np
import tifffile as tff
from PyQt5 import QtWidgets

from juno_custom.scratch.visualisation_utils import VisualisationPlane

import juno_custom.scratch.visualisation_utils as v_utils

from fibsem.structures import (
    BeamType,
    FibsemImage,
    Point,
)
from PyQt5.QtCore import pyqtSignal
from openlm.ui.qt import VisualisationLayerWidget
from openlm.ui.IndividualLayerWidget import IndividualLayerWidget


import logging


class VisualisationLayerWidget(VisualisationLayerWidget.Ui_Form, QtWidgets.QDialog):
    def __init__(
        self,
        viewer: napari.Viewer,
    ):
        super(VisualisationLayerWidget, self).__init__()
        self.setupUi(self)
        self.viewer = viewer
        self.setup_connections()

    def setup_connections(self):
        self.pushButton_VIEW_EM.clicked.connect(
            lambda: v_utils.set_camera_angle(self.viewer, v_utils.ANGLES_EM)
        )
        self.pushButton_VIEW_FIB.clicked.connect(
            lambda: v_utils.set_camera_angle(self.viewer, v_utils.ANGLES_FIB)
        )

    def add_tab(self, viewer: napari.Viewer, visualisation_plane: VisualisationPlane):
        tab = IndividualLayerWidget(
            viewer=viewer, visualisation_plane=visualisation_plane
        )

        from PyQt5.QtWidgets import QSlider

        qslider = QSlider()

        qslider.valueChanged.connect(tab.horizontalSlider_x.setValue)
        self.setup_tab_connections(
            tab=tab, visualisation_plane=visualisation_plane, viewer=viewer
        )
        self.tabWidget_Layers.addTab(tab, tab.name)

    def setup_tab_connections(
        self,
        tab: IndividualLayerWidget,
        visualisation_plane: VisualisationPlane,
        viewer: napari.Viewer,
    ):
        tab.horizontalSlider_x.valueChanged.connect(
            lambda: self.move_plane(
                tab=tab, visualisation_plane=visualisation_plane, viewer=viewer
            )
        )
        tab.horizontalSlider_y.valueChanged.connect(
            lambda: self.move_plane(
                tab=tab, visualisation_plane=visualisation_plane, viewer=viewer
            )
        )
        tab.horizontalSlider_z.valueChanged.connect(
            lambda: self.move_plane(
                tab=tab, visualisation_plane=visualisation_plane, viewer=viewer
            )
        )

        tab.pushButton_x.clicked.connect(lambda: tab.horizontalSlider_x.setValue(50))
        tab.pushButton_y.clicked.connect(lambda: tab.horizontalSlider_y.setValue(50))
        tab.pushButton_z.clicked.connect(lambda: tab.horizontalSlider_z.setValue(50))

    def move_plane(
        self,
        tab: IndividualLayerWidget,
        visualisation_plane: VisualisationPlane,
        viewer: napari.Viewer,
    ):
        # read all three sliders
        # convert to percentage
        x, y, z = (
            tab.horizontalSlider_x.value(),
            tab.horizontalSlider_y.value(),
            tab.horizontalSlider_z.value(),
        )
        tab.move_plane(x, y, z, visualisation_plane=visualisation_plane, viewer=viewer)


def main(config_path=None):
    viewer = napari.Viewer(ndisplay=3)
    vis_ui = VisualisationLayerWidget(viewer=viewer)
    viewer.window.add_dock_widget(
        vis_ui,
        area="right",
        add_vertical_stretch=True,
        name="Cross Correlation Visualiser",
    )

    if config_path is None:
        config = v_utils.read_config(
            r"C:\Users\User\Github\openCLEM\openlm\config\vis_config.yml"
        )
    else:
        config = v_utils.read_config(config_path)

    layers = []

    for image in config["images"]:
        layers.append(v_utils.create_plane_layer(layer_dict=image))

    for layer in layers:
        v_utils.place_plane_image(viewer=viewer, visualisation_plane=layer)
        vis_ui.add_tab(viewer=viewer, visualisation_plane=layer)

    napari.run()


if __name__ == "__main__":
    main()

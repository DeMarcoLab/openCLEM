import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from juno_custom.scratch.ui.qt import IndividualLayerWidget
from juno_custom.scratch.visualisation_utils import VisualisationPlane


class IndividualLayerWidget(IndividualLayerWidget.Ui_Form, QtWidgets.QDialog):
    def __init__(self, viewer: napari.Viewer, parent=None, visualisation_plane=None):
        super(IndividualLayerWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.parent = parent
        self.viewer = viewer
        self.visualisation_plane = visualisation_plane
        self.name = self.visualisation_plane.image.metadata.image_settings.label

    def move_plane(
            self, x: float, y: float, z: float, visualisation_plane: VisualisationPlane, viewer: napari.Viewer
    ):
        origin_position = visualisation_plane.origin_position
        delta_x, delta_y, delta_z = x - 50, y - 50, z - 50
        # TODO: Maybe figure out why y/z are flipped here
        shift_x = delta_x / 100 * visualisation_plane.image.data.shape[2]
        shift_y = delta_z / 100 * visualisation_plane.image.data.shape[1]
        shift_z = delta_y / 100 * visualisation_plane.image.data.shape[1]

        # # # # scale shift_y and shift_z based on the angle of the plane
        angle = np.deg2rad(visualisation_plane.sample_tilt)
        print(f"angle: {angle}")

        move_x = shift_x
        move_y = shift_z * np.cos(angle) - shift_y * np.sin(angle)
        move_z = shift_y * np.cos(angle) + shift_z * np.sin(angle)

        # 'x' is along axis 2
        viewer.layers[visualisation_plane.image.metadata.image_settings.label].translate = origin_position + (move_z, move_y, move_x)

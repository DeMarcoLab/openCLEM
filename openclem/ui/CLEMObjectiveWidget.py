import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from openclem import constants, utils
from openclem.detector import Detector
from openclem.laser import Laser, LaserController
from openclem.structures import ImageSettings, LaserControllerSettings, LaserSettings
from openclem.ui.qt import CLEMObjectiveWidget
from openclem.objective import ObjectiveStage


class CLEMObjectiveWidget(CLEMObjectiveWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        objective: ObjectiveStage,
        viewer: napari.Viewer = None,
        parent=None,
    ):
        super(CLEMObjectiveWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.objective = objective

        self.setup_connections()

        self.update_ui()

    def setup_connections(self):
        print("setup_connections")

        self.pushButton_get_position.clicked.connect(self.get_position)
        self.pushButton_save_position.clicked.connect(self.save_position)
        self.pushButton_move_absolute.clicked.connect(self.move_absolute)
        self.pushButton_move_relative_down.clicked.connect(self.move_relative)
        self.pushButton_move_relative_up.clicked.connect(self.move_relative)

        # dont allow editing
        self.doubleSpinBox_current_position.setEnabled(False)
        self.doubleSpinBox_saved_position.setEnabled(False)

    def update_ui(self):
        print("update_ui")

        self.doubleSpinBox_current_position.setValue(
            self.objective.position * constants.SI_TO_MICRO
        )

        if self.objective.saved_position is not None:
            self.doubleSpinBox_saved_position.setValue(
                self.objective.saved_position * constants.SI_TO_MICRO
            )

    def get_position(self):
        print("get_position")
        print(f"Position: {self.objective.position:.2e}")

        self.update_ui()

        return self.objective.position

    def save_position(self):
        print("save_position")
        self.objective.save_position(self.objective.position)
        print(f"Saved position: {self.objective.saved_position:.2e}")
        self.update_ui()

    def move_absolute(self):
        print("move_absolute")

        abs_position = (
            self.doubleSpinBox_absolute_position.value() * constants.MICRO_TO_SI
        )
        print(f"Absolute position: {abs_position:.2e}")

        self.objective.absolute_move(abs_position)
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

        print(f"Relative position: {relative_position:.2e}, ({direction})")

        self.objective.relative_move(relative_position)

        self.update_ui()


def main():
    from openclem.objectives.demo.demo import DemoObjective
    obj = DemoObjective("demo")
    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMObjectiveWidget(viewer=viewer, objective=obj)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

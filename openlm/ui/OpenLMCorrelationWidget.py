import logging

import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets
import tifffile as tf
logging.basicConfig(level=logging.INFO)

import logging
from copy import deepcopy
import napari
import napari.utils.notifications
import numpy as np
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from openlm import constants, utils
from openlm.microscope import LightMicroscope

from openlm.ui.qt import OpenLMCorrelationWidget

class OpenLMCorrelationWidget(OpenLMCorrelationWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
            self,
            viewer: napari.Viewer = None,
            microscope: LightMicroscope = None,
            parent=None,
    ):
        super(OpenLMCorrelationWidget, self).__init__(parent=parent)
        self.setupUi(self)
        self.parent = parent
        self.viewer = viewer
        # TODO: add fibsem microscope
        self.microscope = microscope
        self.points_1 = []
        self.points_2 = []

        # TODO: make better
        self.load_images()
        self.initialise_viewer()
        self.setup_connections()
    
    def setup_connections(self):
        self.pushButton_correlate.clicked.connect(self.correlate)

    def correlate(self):
        print(self.tableWidget_cpoints.rowCount())
        self.update_cpoints_table()
        # table_widget = QTableWidget()
        # row = table_widget.insertRow(0)
        # table = self.tableWidget_cpoints
        # rowPosition = table.rowCount()
        # table.insertRow(rowPosition)
        # table.setItem(rowPosition, 0, QTableWidgetItem("text1"))
        # table.setItem(rowPosition, 1, QTableWidgetItem("text2"))
        # table.setItem(rowPosition, 2, QTableWidgetItem("text3"))

    def update_cpoints_table(self):
        n_points = np.max([len(self.points_1), len(self.points_2)])
        self.tableWidget_cpoints.setRowCount(0)


        for i in range(n_points):
            if i > len(self.points_1)-1:
                x1 = np.NaN
                y1 = np.NaN
            else:
                x1 = self.points_1[i][1]
                y1 = self.points_1[i][0]

            if i > len(self.points_2)-1:
                x2 = np.NaN
                y2 = np.NaN
            else:
                x2 = self.points_2[i][1] - self.viewer.layers['image_2'].extent.world[0][1]
                y2 = self.points_2[i][0]

            self.tableWidget_cpoints.insertRow(i)
            self.tableWidget_cpoints.setItem(i, 0, QTableWidgetItem(str(x1)))
            self.tableWidget_cpoints.setItem(i, 1, QTableWidgetItem(str(y1)))
            self.tableWidget_cpoints.setItem(i, 2, QTableWidgetItem(str(x2)))
            self.tableWidget_cpoints.setItem(i, 3, QTableWidgetItem(str(y2)))

    
    def initialise_viewer(self):
        self.viewer.add_image(self.image_1, name='image_1', colormap="gray", visible=True)
        self.viewer.add_image(self.image_2, name='image_2', colormap="gray", visible=True, translate=[0, self.viewer.layers['image_1'].data.shape[1]])
        self.setup_callbacks(self.viewer.layers['image_1'])
        self.setup_callbacks(self.viewer.layers['image_2'])

    def setup_callbacks(self, layer):
        layer.mouse_drag_callbacks.append(self._drag_check)

    def _changed(self, layer, event):
        print(event)

    def _check_cpoints_list(self):
        len_points_1 = len(self.points_1)
        len_points_2 = len(self.points_2)
        if len_points_1 == len_points_2:
            return True
        elif len_points_1 > len_points_2:
            return "points_2"
        elif len_points_1 < len_points_2:
            return "points_1"
        else:
            return None     

    def _drag_check(self, layer, event):
        dragged = False
        yield
        # on move
        while event.type == 'mouse_move':
            dragged = True
            yield
        # on release
        if dragged:
            return 
        else:
            self._single_click(layer, event)
            return
    
    def _single_click(self, layer, event):

        if event.button == 1:
            return

        clicked_layer = self._check_layer_clicked(event)
        if clicked_layer is None:
            return

        if clicked_layer == self.viewer.layers['image_1']:
            if self._check_cpoints_list() not in ["points_1", True]:
                return       
            if 'points_1' in self.viewer.layers:
                self.points_1.append(event.position)
                self.viewer.layers['points_1'].data = self.points_1
            else:
                self.viewer.add_points(event.position, name='points_1')
                self.points_1 = [event.position]
                self.setup_callbacks(self.viewer.layers['points_1'])
                # self.viewer.layers['points_1'].events.data.connect(self._changed)

        if clicked_layer == self.viewer.layers['image_2']:
            if self._check_cpoints_list() not in ["points_2", True]:
                return
            if 'points_2' in self.viewer.layers:
                self.points_2.append(event.position)
                self.viewer.layers['points_2'].data = self.points_2
            else:
                    self.viewer.add_points(event.position, name='points_2')
                    self.points_2 = [event.position]
                    self.setup_callbacks(self.viewer.layers['points_2'])

    def _check_layer_clicked(self, event):
        extent_image_1 = self.viewer.layers['image_1'].extent.world
        extent_image_2 = self.viewer.layers['image_2'].extent.world

        image_1_x = [extent_image_1[0][1], extent_image_1[1][1]]
        image_1_y = [extent_image_1[0][0], extent_image_1[1][0]]

        image_2_x = [extent_image_2[0][1], extent_image_2[1][1]]
        image_2_y = [extent_image_2[0][0], extent_image_2[1][0]]

        click_x = event.position[1]
        click_y = event.position[0]

        click_within_image_1 = (click_x > image_1_x[0] and click_x < image_1_x[1]) and (click_y > image_1_y[0] and click_y < image_1_y[1])
        click_within_image_2 = (click_x > image_2_x[0] and click_x < image_2_x[1]) and (click_y > image_2_y[0] and click_y < image_2_y[1])

        if click_within_image_1:
            return self.viewer.layers['image_1']
        if click_within_image_2:
            return self.viewer.layers['image_2']        
        return None

    def load_images(self):
        # TODO: make this dynamic
        """Forcefully load images from hard drive"""
        self.image_1 = tf.imread(r"Y:\Projects\piescope\piescope_dev\tile\2023-05-08-03-58-01-001792PM.tif")
        self.image_1 = self.image_1[:, :, 0]

        self.image_2 = tf.imread(r"Y:\Projects\piescope\piescope_dev\tile\2023-05-08-03-58-09-153392PM.tif")
        self.image_2 = self.image_2[:, :, 0]


def main():
    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = OpenLMCorrelationWidget(viewer=viewer)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

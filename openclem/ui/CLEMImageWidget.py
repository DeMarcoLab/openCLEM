import napari
import napari.utils.notifications
from PyQt5 import QtWidgets

from openclem.ui.qt import CLEMImageWidget

import numpy as np
from pathlib import Path
from openclem.structures import ImageSettings
from openclem.detector import Detector
from openclem.laser import LaserController, Laser
from openclem import constants, utils

from openclem.ui.CLEMDetectorWidget import CLEMDetectorWidget
from openclem.ui.CLEMLaserWidget import CLEMLaserWidget

class CLEMImageWidget(CLEMImageWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        viewer: napari.Viewer = None,
        det_widget: CLEMDetectorWidget = None,
        laser_widget: CLEMLaserWidget = None,
        parent=None,
    ):
        super(CLEMImageWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.det_widget = det_widget
        self.laser_widget = laser_widget

        self.setup_connections()

        # self.laser_controller, self.detector = utils.setup_session()

    def setup_connections(self):

        self.pushButton_acquire_image.clicked.connect(self.acquire_image)
        self.comboBox_imaging_format.addItems(["tiff", "png", "jpg", "zarr"])
        self.comboBox_imaging_mode.addItems(["Single", "Live"])

    def get_settings_from_ui(self):

        print("get_settings_from_ui")

        image_settings = ImageSettings(
            pixel_size=1e-9,
            exposure=self.doubleSpinBox_exposure.value() * constants.MILLI_TO_SI,
            image_format=self.comboBox_imaging_format.currentText(),
        )

        return image_settings


    def acquire_image(self):

        image_settings = self.get_settings_from_ui()

        detector_settings = self.det_widget.get_detector_settings_from_ui()
        detector = self.det_widget.detector
        detector.init_camera()

        laser_settings = self.laser_widget.get_laser_settings_from_ui()
        lc = self.laser_widget.lc

        print(f"----------- acquire_image -----------")
        print(f"image_settings: {image_settings}")
        print(f"detector_settings: {detector_settings}")
        print(f"laser_settings: {laser_settings}")

        # TODO: actual image acquisition
        image = detector.grab_image(image_settings=image_settings)

        self.update_viewer(image, "image")

    def update_viewer(self, arr: np.ndarray, name: str):

        if name in self.viewer.layers:
            self.viewer.layers[name].data = arr
        else:
            self.viewer.add_image(arr, name=name)


    def closeEvent(self, event):
        self.viewer.layers.clear()
        event.accept()


def main():

    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = CLEMImageWidget(viewer=viewer)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

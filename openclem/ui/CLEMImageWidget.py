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

from openclem.ui import CLEMHardwareWidget
from napari.qt.threading import thread_worker
from openclem.microscope import LightMicroscope



class CLEMImageWidget(CLEMImageWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        hardware_widget: CLEMHardwareWidget,
        viewer: napari.Viewer,
        parent=None,
    ):
        super(CLEMImageWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self.hardware_widget = hardware_widget
        self._ACQUIRE_IMAGES = False


        self.setup_connections()


    def setup_connections(self):

        self.pushButton_acquire_image.clicked.connect(self.pushButton_acquire_image_clicked)
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


    def pushButton_acquire_image_clicked(self):
        print("pushButton_acquire_image_clicked")

        # toggle ACQUIRE_IMAGES
        if self._ACQUIRE_IMAGES:
            self._ACQUIRE_IMAGES = False
            return
        


        image_settings = self.get_settings_from_ui()
        microscope: LightMicroscope = self.hardware_widget.microscope
        microscope._detector.init_camera() # TODO: move to microscope
        detector_settings = microscope._detector.settings
        laser_settings = microscope._laser_controller.settings
        
        print(f"----------- acquire_image -----------")
        print(f"image_settings: {image_settings}")
        print(f"detector_settings: {detector_settings}")
        print(f"laser_settings: {laser_settings}")


        if self.comboBox_imaging_mode.currentText() == "Single":
            self.acquire_image(microscope, image_settings)
        elif self.comboBox_imaging_mode.currentText() == "Live":
            self.live_image(microscope, image_settings)

    def acquire_image(self, microscope: LightMicroscope, image_settings: ImageSettings):

        # TODO: actual image acquisition
        image = microscope.acquire_image(image_settings)

        self.update_viewer(image, "image")

    def live_image(self, microscope: LightMicroscope, image_settings: ImageSettings):
        
        self.pushButton_acquire_image.setText("Acquiring...")
        self.pushButton_acquire_image.setStyleSheet("background-color: orange")
        
        self._ACQUIRE_IMAGES = True

        # TODO: disable other microscope interactions
        worker = self.run_live_image(microscope, image_settings)
        worker.returned.connect(self.live_image_finished)  # type: ignore
        worker.yielded.connect(self.update_live)  # type: ignore
        worker.start()

    @thread_worker
    def run_live_image(self, microscope: LightMicroscope, image_settings: ImageSettings):

        # TODO: update image settings while live...
        import time
        while self._ACQUIRE_IMAGES:
            
            time.sleep(0.1)
            image = microscope.acquire_image(image_settings)
            
            yield (image, "image")

    def update_live(self, result):
        image, name = result
        self.update_viewer(image, name)

    def live_image_finished(self):
        self.pushButton_acquire_image.setText("Acquire Image")
        self.pushButton_acquire_image.setStyleSheet("background-color: green")


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

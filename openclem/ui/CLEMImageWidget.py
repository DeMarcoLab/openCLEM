import napari
import napari.utils.notifications
from PyQt5 import QtWidgets

from openclem.ui.qt import CLEMImageWidget

import numpy as np
from pathlib import Path
from openclem.structures import ImageSettings, ImageFormat, ImageMode, TriggerEdge
from openclem import constants, utils


from openclem.ui import CLEMHardwareWidget
from napari.qt.threading import thread_worker
from openclem.microscope import LightMicroscope
from PIL import Image
import logging
from openclem.structures import SynchroniserMessage
import time
import threading


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
        self.stop_event = threading.Event()
        self.stop_event.set()

        self.setup_connections()


    def setup_connections(self):

        self.pushButton_acquire_image.clicked.connect(self.pushButton_acquire_image_clicked)
        self.comboBox_imaging_format.addItems([format.name for format in ImageFormat])
        self.comboBox_imaging_mode.addItems([mode.name for mode in ImageMode])

        microscope: LightMicroscope = self.hardware_widget.microscope

        self.emission_dict = {}
        for i, laser in enumerate(microscope.get_laser_controller().lasers):
            
            self.emission_dict[laser] = QtWidgets.QSpinBox()
            self.emission_dict[laser].setMinimum(0)
            self.emission_dict[laser].setMaximum(1000000)

            self.emission_dict[laser].setValue(1000)
            # self.emission_dict[laser].setValue(microscope.get_laser_controller().get(laser))

            self.gridLayout_laser_emission.addWidget(QtWidgets.QLabel(laser), i, 0)
            self.gridLayout_laser_emission.addWidget(self.emission_dict[laser], i, 1)

    def get_settings_from_ui(self):

        image_settings = ImageSettings(
            pixel_size=1e-9,
            exposure=self.doubleSpinBox_exposure.value() * constants.MILLI_TO_SI,
            image_format=ImageFormat[self.comboBox_imaging_format.currentText()],
            mode=ImageMode[self.comboBox_imaging_mode.currentText()],
        )

        sync_message = SynchroniserMessage(
            exposures=[v.value() for v in self.emission_dict.values()],
            pins={"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4}, # TODO actually do something
            mode = image_settings.mode,
            n_slices=4,
            trigger_edge=TriggerEdge.RISING,
        )
        return image_settings, sync_message


    def pushButton_acquire_image_clicked(self):

        # toggle ACQUIRE_IMAGES
        if not self.stop_event.is_set():
            self.stop_event.set()
            logging.info("Stopping Image Acquistion")
            return
        else:
            self.stop_event.clear()
            self.pushButton_acquire_image.setText("Acquiring...")
            self.pushButton_acquire_image.setStyleSheet("background-color: orange")
        
        image_settings, sync_message = self.get_settings_from_ui()
        microscope: LightMicroscope = self.hardware_widget.microscope
        microscope.setup_acquisition()
        
        # TODO: disable other microscope interactions
        worker = self.update_live_image()
        worker.finished.connect(self.update_live_finished)  # type: ignore
        worker.yielded.connect(self.update_live)  # type: ignore
        worker.start()
        
        # TODO: single image does not update the viewer? too fast?

        # Set up sync
        synchroniser_message = SynchroniserMessage.__from_dict__({
            "exposures": [1000, 1000, 1000, 1000],
            "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
            "mode": image_settings.mode.value,
            "n_slices": 4,
            "trigger_edge": "RISING",
        })

        assert synchroniser_message == sync_message, "Synchroniser message does not match"

        self.image_queue, self.stop_event = microscope.acquire_image(
            image_settings=image_settings, 
            sync_message=synchroniser_message,
            stop_event=self.stop_event
            )
        


    @thread_worker
    def update_live_image(self):
        import time
        try:
            # wait for the first image to be acquired
            # while self.stop_event is None:
            #     logging.info(f"Waiting for acquisition to start...")
            #     time.sleep(0.1)

            while self.image_queue.qsize() > 0 or not self.stop_event.is_set():
                
                image = self.image_queue.get()
                logging.info(f"Getting image from queue: {image.shape}, {np.mean(image)}")

                yield (image, "image")

        except Exception as e:
            logging.error(e)
        return

    def update_live(self, result):
        image, name = result
        self.update_viewer(image, name)

    def update_live_finished(self):
        self.pushButton_acquire_image.setText("Acquire Image")
        self.pushButton_acquire_image.setStyleSheet("background-color: green")

    def update_viewer(self, arr: np.ndarray, name: str):
        logging.info(f"Updating viewer: {arr.shape}, {name}")
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

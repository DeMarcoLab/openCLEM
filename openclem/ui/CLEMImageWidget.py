import logging
import threading
import time
from pathlib import Path

import napari
import napari.utils.notifications
import numpy as np
from napari.qt.threading import thread_worker
from PyQt5 import QtWidgets

from openclem import constants
from openclem.microscope import LightMicroscope
from openclem.structures import (
    ImageFormat,
    ImageMode,
    ImageSettings,
    SynchroniserMessage,
    TriggerEdge,
)
from openclem.ui import CLEMHardwareWidget
from openclem.ui.qt import CLEMImageWidget

from copy import deepcopy

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
        # grid mode on
        self.viewer.grid.enabled = True

        self.hardware_widget = hardware_widget
        self.stop_event = threading.Event()
        self.stop_event.set()

        self.setup_connections()

    def setup_connections(self):
        self.pushButton_acquire_image.clicked.connect(
            self.pushButton_acquire_image_clicked
        )

        self.pushButton_update_settings.clicked.connect(
            self.update_imaging_settings
        )
        self.pushButton_update_settings.setVisible(False)
        self.comboBox_imaging_format.addItems([format.name for format in ImageFormat])
        self.comboBox_imaging_mode.addItems([mode.name for mode in ImageMode])

    def get_settings_from_ui(self):
        image_settings = ImageSettings(
            pixel_size=1e-9,
            exposure=self.doubleSpinBox_exposure.value() * constants.MILLI_TO_SI,
            image_format=ImageFormat[self.comboBox_imaging_format.currentText()],
            mode=ImageMode[self.comboBox_imaging_mode.currentText()],
        )

        # get laser exposures
        microscope: LightMicroscope = self.hardware_widget.microscope
        exposure_times = microscope.get_laser_controller().get_exposure_times().values()
        exposures = [int(v *constants.SI_TO_MILLI) for v in exposure_times]

        # number of non zero exposures
        image_settings.n_images = len([v for v in exposures if v > 0])

        sync_message = SynchroniserMessage(
            exposures=exposures,
            pins={
                "laser1": 1,
                "laser2": 2,
                "laser3": 3,
                "laser4": 4,
            },  # TODO actually do something
            mode=image_settings.mode,
            n_slices=image_settings.n_images,# TODO: get from UI
            trigger_edge=TriggerEdge.RISING, # TODO: get from UI
        )
        return image_settings, sync_message

    def update_imaging_settings(self):
        print("UPDATE SETTINGS")
        
        image_settings, sync_message = self.get_settings_from_ui()
        microscope: LightMicroscope = self.hardware_widget.microscope
        
        microscope.get_synchroniser().stop_sync()
        microscope.get_synchroniser().sync_image(sync_message)

    def pushButton_acquire_image_clicked(self):

        # check if acquisition is already running
        if not self.stop_event.is_set():
            self.stop_event.set()
            microscope: LightMicroscope = self.hardware_widget.microscope
            microscope.get_synchroniser().stop_sync()
            logging.info("Stopping Image Acquistion")
            # self.pushButton_update_settings.setVisible(False)
            return
        else:
            self.stop_event.clear()
            # self.pushButton_update_settings.setVisible(True)
            self.pushButton_acquire_image.setText("Acquiring...")
            self.pushButton_acquire_image.setStyleSheet("background-color: orange")

        image_settings, sync_message = self.get_settings_from_ui()
        microscope: LightMicroscope = self.hardware_widget.microscope
        microscope.setup_acquisition()

        # TODO: disable other microscope interactions
        worker = self.update_live_image()
        worker.returned.connect(self.update_live_finished)  # type: ignore
        worker.yielded.connect(self.update_live)  # type: ignore
        worker.start()

        # acquire image
        self.image_queue, self.stop_event = microscope.acquire_image( # TODO: move imgage queue and stop_event to microscope
            image_settings=image_settings,
            sync_message=sync_message,
            stop_event=self.stop_event,
        )

    @thread_worker
    def update_live_image(self):
        try:
            
            counter = 0
            while self.image_queue.qsize() > 0 or not self.stop_event.is_set():
                
                image = self.image_queue.get()
                # logging.info(
                #     f"Getting image from queue: {image.shape}, {np.mean(image):.2f}"
                # )

                # TODO: construct actual image with metadata
                yield (image, f"Channel {counter % 4:02d}")
                counter +=1

        except Exception as e:
            logging.error(e)
        return

    def update_live(self, result):
        image, name = result
        self.update_viewer(image, name)

    def update_live_finished(self):
        # self.pushButton_update_settings.setVisible(False)
        self.pushButton_acquire_image.setText("Acquire Image")
        self.pushButton_acquire_image.setStyleSheet("background-color: green")

    def update_viewer(self, arr: np.ndarray, name: str):
        if name in self.viewer.layers:
            self.viewer.layers[name].data = arr
        else:

            # TODO: missing red
            if name == "Channel 00":
                color = "red"
            if name == "Channel 01":
                color = "green"
            if name == "Channel 02":
                color = "cyan"
            if name == "Channel 03":
                color = "magenta"

            self.viewer.add_image(arr, name=name, opacity=1.0, blending="translucent", colormap=color)

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

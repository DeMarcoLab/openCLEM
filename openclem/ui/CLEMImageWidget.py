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
    LightImage
)
from openclem.ui import CLEMHardwareWidget
from openclem.ui.qt import CLEMImageWidget

from copy import deepcopy

import vispy.color as v_color


try:
    from fibsem import utils, conversions, constants
    from fibsem.structures import Point, BeamType
    FIBSEM = True
except ImportError:
    FIBSEM = False


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
        self.image = None
        # grid mode on
        # self.viewer.grid.enabled = True

        self.hardware_widget = hardware_widget
        self.stop_event = threading.Event()
        self.stop_event.set()

        self.setup_connections()

        if FIBSEM:
            self.microscope, self.settings = utils.setup_session()


    def setup_connections(self):
        self.pushButton_acquire_image.clicked.connect(
            self.pushButton_acquire_image_clicked
        )

        self.comboBox_imaging_mode.addItems([mode.name for mode in ImageMode])

        self.pushButton_save_image.clicked.connect(self.save_image)

    def save_image(self):
        
        if self.image is None:
            napari.utils.notifications.show_info(f"No image to save")
            return 
        
        import os
        label = f"{self.lineEdit_save_label.text()}_{self.image.metadata.time}"
        
        fname = os.path.join(label)
        self.image.save(fname)
        napari.utils.notifications.show_info(f"Saved image to {fname}")

 
    def get_settings_from_ui(self):
        image_settings = ImageSettings(
            pixel_size=1e-9, 
            exposure=0.25, # Software exposure...
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
            # microscope: LightMicroscope = self.hardware_widget.microscope
            self.lm.get_synchroniser().stop_sync()
            logging.info("Stopping Image Acquistion")
            # self.pushButton_update_settings.setVisible(False)
            return
        else:
            self.stop_event.clear()
            # self.pushButton_update_settings.setVisible(True)
            self.pushButton_acquire_image.setText("Acquiring...")
            self.pushButton_acquire_image.setStyleSheet("background-color: orange")

        image_settings, sync_message = self.get_settings_from_ui()
        self.lm: LightMicroscope = self.hardware_widget.microscope
        self.lm.setup_acquisition()

        # TODO: disable other microscope interactions
        worker = self.lm.consume_image_queue_ui()
        worker.returned.connect(self.update_live_finished)  # type: ignore
        worker.yielded.connect(self.update_live)  # type: ignore
        worker.start()

        # acquire image
        self.image_queue, self.stop_event = self.lm.acquire_image( 
            image_settings=image_settings,
            sync_message=sync_message,
            stop_event=self.stop_event,
        )

    def update_live(self, result: LightImage):

            
        self.image = result
        info = {}

        for i, laser in enumerate(self.image.metadata.lasers):
            info[i] = {
                "color": v_color.Colormap([[0, 0, 0], laser.color]),
                "display_name": f"Channel {int(laser.wavelength)}nm"
            }

        for i, channel in enumerate(self.image.metadata.channels):
            self.update_viewer(self.image.data[:, :, i], info[channel]["display_name"], info[channel]["color"])

    def update_live_finished(self):
        self.pushButton_acquire_image.setText("Acquire Image")
        self.pushButton_acquire_image.setStyleSheet("background-color: green")

    def update_viewer(self, arr: np.ndarray, name: str, color: str):
        if name in self.viewer.layers:
            self.viewer.layers[name].data = arr
        else:

            layer = self.viewer.add_image(data=arr, 
                                        name=name, 
                                        opacity=0.7, 
                                        blending="additive", 
            )
            layer.colormap = name, color

            # register mouse callbacks
            layer.mouse_double_click_callbacks.append(self._double_click)

            # add crosshair at the image centre coordiantes
            if "crosshair" not in self.viewer.layers:
                self.viewer.add_points(
                    np.array([[arr.shape[1] / 2, arr.shape[0] / 2]]),
                    symbol="cross",
                    size=50,
                    edge_color="white",
                    face_color="white",
                    name="crosshair",
                )


    def _double_click(self, layer, event):

        # get coords
        coords = layer.world_to_data(event.position)

        # TODO: dimensions are mixed which makes this confusing to interpret... resolve
        coords, beam_type, image = self.get_data_from_coord(coords)

        if beam_type is None:
            napari.utils.notifications.show_info(
                f"Clicked outside image dimensions. Please click inside the image to move."
            )
            return

        if FIBSEM is False:
            return


        # image = self.image
        nominal_pixelsize = 6.5e-6 / 20 #/ 2.94 # PATENTED_TECHNOLOGY
        pixelsize = 125e-6 / 350 # MEASURED

        # 6.5um/20px = 0.325 um/px
        #125um/350px = 0.35714285714285715 um/px
        # 1/0.35714285714285715 = 2.8 px/um

        point = conversions.image_to_microscope_image_coordinates(
            Point(x=coords[1], y=coords[0]), image, pixelsize,
        )
        logging.info(f"IMAGE: {image.shape}, PIXELSIZE: {pixelsize:.2e}")

        logging.info(
            f"Movement: STABLE | COORD {coords} | SHIFT {point.x:.2e}, {point.y:.2e} | {beam_type}"
        )

        logging.info(f"Microscope Stage Position: {self.microscope.get_stage_position()}")
        # TODO: we need a fibsem microscope
        self.microscope.stable_move(
                settings=self.settings,
                dx=point.x,
                dy=point.y,
                beam_type=BeamType.ION,
            )
        logging.info(f"Microscope Stage Position: {self.microscope.get_stage_position()}")



    def get_data_from_coord(self, coords: tuple) -> tuple:
        # check inside image dimensions, (y, x)
        # eb_shape = self.eb_image.data.shape[0], self.eb_image.data.shape[1]
        # ib_shape = self.ib_image.data.shape[0], self.ib_image.data.shape[1] + self.eb_image.data.shape[1]

        if (coords[0] > 0 and coords[0] < self.image.data.shape[0]) and (
            coords[1] > 0 and coords[1] < self.image.data.shape[1]
        ):
            beam_type = "LIGHT"
            image = self.image.data[:, :, 0]
        else:
            beam_type, image = None, None

        return coords, beam_type, image

        # all the images are the same size, based on detector...
        # always light
        # turn grid off to make this eaiser?

    # TODO: ui upgrades
    # toggle grid / opacity to show all channels

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

import logging
import threading

import napari
import napari.utils.notifications
import numpy as np
import vispy.color as v_color
from PyQt5 import QtWidgets

from openlm import constants
from openlm.microscope import LightMicroscope
from openlm.structures import (ImageMode, ImageSettings, LightImage,
                                 SynchroniserMessage, TriggerEdge)
from openlm.ui import OpenLMHardwareWidget
from openlm.ui.qt import OpenLMImageWidget

try:
    from fibsem import constants, conversions, utils
    from fibsem.structures import BeamType, Point, FibsemStagePosition
    FIBSEM = True
except ImportError:
    FIBSEM = False


class OpenLMImageWidget(OpenLMImageWidget.Ui_Form, QtWidgets.QWidget):
    def __init__(
        self,
        hardware_widget: OpenLMHardwareWidget,
        viewer: napari.Viewer,
        parent=None,
    ):
        super(OpenLMImageWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.viewer = viewer
        self._n_layers = len(self.viewer.layers)
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

        self.pushButton_move_microscope.clicked.connect(self._move_to_microscope)

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
            
            pixelsize = 125e-6 / 350 * constants.SI_TO_MICRO # MEASURED # microns per pixel
            microns_per_pixel = [pixelsize, pixelsize]
            layer.scale = microns_per_pixel

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
                    scale=microns_per_pixel,
                )

                # add scale bar
                self.viewer.scale_bar.visible = True
                self.viewer.scale_bar.color = "white"
                # update to actual units: https://forum.image.sc/t/setting-scale-bar-units-in-other-than-pixels-real-coordinates/49158/12
                # NB: i think this might break click to move
                self.viewer.scale_bar.unit = "um"

        # reorder layers
        if self._n_layers != len(self.viewer.layers):
            self._n_layers = len(self.viewer.layers)
            self._reorder_layers()
        
    def _reorder_layers(self):
        logging.info(f"Layers are being reordered")
        # get list of layer names, and order them alphabetically, using the index
        layer_names = sorted([layer.name for layer in self.viewer.layers])
        new_order = [layer_names.index(layer.name) for layer in self.viewer.layers]
        self.viewer.layers.move_multiple(new_order)

        # centre the camera on the active layer, adjusting for scaling
        image_centre = (self.viewer.layers[-1].data.shape[1] / 2, self.viewer.layers[-1].data.shape[0] / 2)# type: ignore
        cam_centre = self.viewer.layers[-1].data_to_world(image_centre)
        self.viewer.camera.center = cam_centre
        self.viewer.camera.zoom = 1.0

    def _move_to_microscope(self):

        # TODO: fully implement this when have hardware
        _translation = {"x": 49.6167e-3, "y": -0.339e-3, "z": 0.137e-3} # TODO: move to config
        
        current_position_x = self.microscope.get_stage_position().x
        # current_position_x = np.random.choice([np.random.randint(-10, 10), np.random.randint(40, 60)])

        fibsem_min = -10.e-3
        fibsem_max = 10.e-3
        lm_min = 40.e-3
        lm_max = 60.e-3

        x = _translation["x"]
        y = _translation["y"]
        z = _translation["z"]
        
        logging.info(f"Current position: {current_position_x}")
        msg: str
        if fibsem_min < current_position_x < fibsem_max:
           msg = 'Under FIBSEM, moving to light microscope'
        elif lm_min < current_position_x < lm_max:
            x = -x
            y = -y
            z = -z
            msg = 'Under light microscope, moving to FIBSEM'
        else:
            logging.warn('Not positioned under the either microscope, cannot move to other microscope')
            return

        logging.info(msg)
        napari.utils.notifications.show_info(msg)

        logging.info(f"Moving to microscope: x={x}, y={y}, z={z}")
        new_position = FibsemStagePosition(x=x, y=y, z=z, r=0, t=0)
        # self.microscope.stable_move(new_position, beamtype=BeamType.ION)
        self.microscope.move_stage_relative(new_position)

        
        if FIBSEM is False:
            msg = f"Stage Movement is disabled (No OpenFIBSEM)"
            napari.utils.notifications.show_info(msg)
            logging.info(msg)
            return   


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
            msg = f"Stage Movement is disabled (No OpenFIBSEM): Coords: {coords[0]:.2f}, {coords[1]:.2f} "
            napari.utils.notifications.show_info(msg)
            logging.info(msg)
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
        self.microscope.stable_move(
                settings=self.settings,
                dx=point.x,
                dy=point.y,
                beam_type=BeamType.ION,
            )
        logging.info(f"Microscope Stage Position: {self.microscope.get_stage_position()}")

    def get_data_from_coord(self, coords: tuple) -> tuple:
        # check inside image dimensions, (y, x)
        if (coords[0] > 0 and coords[0] < self.image.data.shape[0]) and (
            coords[1] > 0 and coords[1] < self.image.data.shape[1]
        ):
            beam_type = "LIGHT"
            image = self.image.data[:, :, 0]
        else:
            beam_type, image = None, None

        return coords, beam_type, image

    def closeEvent(self, event):
        self.viewer.layers.clear()
        event.accept()


def main():
    viewer = napari.Viewer(ndisplay=2)
    image_settings_ui = OpenLMImageWidget(viewer=viewer)
    viewer.window.add_dock_widget(
        image_settings_ui, area="right", add_vertical_stretch=False
    )
    napari.run()


if __name__ == "__main__":
    main()

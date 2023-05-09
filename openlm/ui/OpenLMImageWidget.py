import logging
import threading

import napari
import napari.utils.notifications
import numpy as np
import vispy.color as v_color
from PyQt5 import QtWidgets, QtCore

from openlm import constants, utils
from openlm.microscope import LightMicroscope
from openlm.structures import (
    ImageMode,
    ImageSettings,
    LightImage,
    SynchroniserMessage,
    TriggerEdge,
    TileSettings,
)
import os
from openlm.ui import OpenLMHardwareWidget
from openlm.ui.qt import OpenLMImageWidget
from openlm import config as cfg
try:
    from fibsem import constants, conversions
    from fibsem.structures import BeamType, Point, FibsemStagePosition

    FIBSEM = True
except ImportError:
    FIBSEM = False

import time
from openlm.workflow import _gen_tiling_workflow, _gen_volume_workflow, _gen_workflow
from openlm.structures import WorkflowSettings


class OpenLMImageWidget(OpenLMImageWidget.Ui_Form, QtWidgets.QWidget):
    image_signal = QtCore.pyqtSignal(dict)

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

        self.hardware_widget = hardware_widget
        self.stop_event = threading.Event()
        self.stop_event.set()
        self.microscope: LightMicroscope = (
            self.hardware_widget.microscope
        )  # TODO need to check we are updating this correctly

        self.setup_connections()

    def setup_connections(self):
        self.pushButton_acquire_image.clicked.connect(
            self.pushButton_acquire_image_clicked
        )

        self.comboBox_imaging_mode.addItems([mode.name for mode in ImageMode])

        self.pushButton_save_image.clicked.connect(self.save_image)

        self.pushButton_move_microscope.clicked.connect(self._move_to_microscope)

        self.image_signal.connect(self.update_image)

        # workflows
        self.pushButton_run_tiling.clicked.connect(self.run_workflow)

        self.spinBox_tile_n_rows.valueChanged.connect(self.update_workflow_ui)
        self.spinBox_tile_n_cols.valueChanged.connect(self.update_workflow_ui)
        self.doubleSpinBox_tile_dx.valueChanged.connect(self.update_workflow_ui)
        self.doubleSpinBox_tile_dy.valueChanged.connect(self.update_workflow_ui)
        self.spinBox_vol_n_slices.valueChanged.connect(self.update_workflow_ui)
        self.doubleSpinBox_vol_dz.valueChanged.connect(self.update_workflow_ui) 

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
            exposure=0.25,  # Software exposure...
            mode=ImageMode[self.comboBox_imaging_mode.currentText()],
        )

        # get laser exposures
        microscope: LightMicroscope = self.hardware_widget.microscope
        exposure_times = microscope.get_laser_controller().get_exposure_times().values()
        exposures = [int(v * constants.SI_TO_MILLI) for v in exposure_times]

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
            n_slices=image_settings.n_images,  # TODO: get from UI
            trigger_edge=TriggerEdge.RISING,  # TODO: get from UI
        )
        return image_settings, sync_message

    def update_imaging_settings(self):
        print("UPDATE SETTINGS")

        image_settings, sync_message = self.get_settings_from_ui()
        microscope: LightMicroscope = self.hardware_widget.microscope

        microscope.get_synchroniser().stop_sync()
        microscope.get_synchroniser().sync_image(sync_message)

    def pushButton_acquire_image_clicked(self, single_image: bool = False, save=False):
        # check if acquisition is already running
        if not self.stop_event.is_set():
            self.stop_event.set()
            self.microscope.get_synchroniser().stop_sync()
            logging.info("Stopping Image Acquistion")
            return
        else:
            self.stop_event.clear()
            self.pushButton_acquire_image.setText("Acquiring...")
            self.pushButton_acquire_image.setStyleSheet("background-color: orange")

        image_settings, sync_message = self.get_settings_from_ui()
        # self.microscope: LightMicroscope = self.hardware_widget.microscope
        self.microscope.setup_acquisition()

        if single_image:
            image_settings.mode = ImageMode.SINGLE

        # TODO: disable other microscope interactions
        worker = self.microscope.consume_image_queue(parent_ui=self)
        worker.returned.connect(self.update_live_finished)  # type: ignore
        worker.start()

        # acquire image
        self.image_queue, self.stop_event = self.microscope.acquire_image(
            image_settings=image_settings,
            sync_message=sync_message,
            stop_event=self.stop_event,
        )

    def run_workflow(self):
        logging.info(f"Running Workflow")

        self.setup_workflow()

        self.idx = 0
        self.run_workflow_step()

    def update_workflow_ui(self):
        
        workflow_settings = WorkflowSettings(
            n_rows = self.spinBox_tile_n_rows.value(),
            n_cols = self.spinBox_tile_n_cols.value(),
            dx = self.doubleSpinBox_tile_dx.value() * constants.MICRO_TO_SI,
            dy = self.doubleSpinBox_tile_dy.value() * constants.MICRO_TO_SI,
            n_slices = self.spinBox_vol_n_slices.value(),
            dz = self.doubleSpinBox_vol_dz.value() * constants.MICRO_TO_SI,
        )

        return workflow_settings

    def setup_workflow(self):

        mode = ImageMode.SINGLE
        image_settings, sync_message = self.get_settings_from_ui()
        image_settings.mode = mode
        image_settings.n_images = len([v for v in sync_message.exposures if v > 0])

        image_settings.path = os.path.join(cfg.LOG_PATH, f"workflow_{utils.current_timestamp()}")
        os.makedirs(image_settings.path, exist_ok=True)

        image_settings.workflow = self.update_workflow_ui()

        wf = image_settings.workflow

        # This gives us the relative x, y coordinates for each imaging position
        tile_coords = _gen_tiling_workflow(n_rows=wf.n_rows, n_cols=wf.n_cols, dx=wf.dx, dy=wf.dy)

        # This gives us the relative z coordinates for each imaging position
        volume_coords = _gen_volume_workflow(n_slices=wf.n_slices, step_size=wf.dz)

        self.workflow = _gen_workflow(tile_coords, volume_coords, 
                                image_settings=image_settings, 
                                sync_message=sync_message,
                                )

        logging.info(f"Workflow Length: {len(self.workflow)}")

        from collections import Counter
        c = Counter([step["type"] for step in self.workflow])

        self.label_info_1.setText(f"Workflow Length: {len(self.workflow)}")
        self.label_info_2.setText(f"Workflow Steps: {c}")

    def run_workflow_step(self):
        step = self.workflow[self.idx]

        logging.info(f"Running Workflow Step: {step}")

        if step["type"] == "acquire_image":
            self.stop_event.clear()
            self.microscope.setup_acquisition()

            # TODO: disable other microscope interactions
            worker = self.microscope.consume_image_queue(save=True, parent_ui=self)
            worker.returned.connect(self.finish_workflow_step)  # type: ignore
            worker.start()

            time.sleep(1)

            # acquire image
            self.image_queue, self.stop_event = self.microscope.acquire_image(
                image_settings=step["settings"],
                sync_message=step["sync"],
                stop_event=self.stop_event,
            )

        if step["type"] == "move_stage":
            worker = self.microscope.move_stage(dx=step["dx"], dy=step["dy"])
            worker.returned.connect(self.finish_workflow_step)  # type: ignore
            worker.start()

        if step["type"] == "move_objective":
            worker = self.microscope.move_objective_stage(dz=step["dz"])
            worker.returned.connect(self.finish_workflow_step)  # type: ignore
            worker.start()

        if step["type"] == "restore_state":
            logging.info("Restoring Microscope")

    def finish_workflow_step(self):
        logging.info(f"Finished Workflow Step {self.idx+1}")
        self.idx += 1

        if self.idx < len(self.workflow):
            logging.info(f"Workflow: {self.idx+1}/{len(self.workflow)}")
            self.run_workflow_step()
        else:
            logging.info("Finished Workflow")

    def update_image(self, dat: dict):
        self.image = dat["image"]
        info = {}

        for i, laser in enumerate(self.image.metadata.lasers):
            info[i] = {
                "color": v_color.Colormap([[0, 0, 0], laser.color]),
                "display_name": f"Channel {int(laser.wavelength)}nm",
            }

        for i, channel in enumerate(self.image.metadata.channels):
            self.update_viewer(
                self.image.data[:, :, i],
                info[channel]["display_name"],
                info[channel]["color"],
            )

    def update_live_finished(self):
        self.pushButton_acquire_image.setText("Acquire Image")
        self.pushButton_acquire_image.setStyleSheet("background-color: green")

    def update_viewer(self, arr: np.ndarray, name: str, color: str):
        if name in self.viewer.layers:
            self.viewer.layers[name].data = arr
        else:
            layer = self.viewer.add_image(
                data=arr,
                name=name,
                opacity=0.7,
                blending="additive",
            )
            layer.colormap = name, color

            pixelsize = (
                125e-6 / 350 * constants.SI_TO_MICRO
            )  # MEASURED # microns per pixel
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
        image_centre = (self.viewer.layers[-1].data.shape[1] / 2, self.viewer.layers[-1].data.shape[0] / 2)  # type: ignore
        cam_centre = self.viewer.layers[-1].data_to_world(image_centre)
        self.viewer.camera.center = cam_centre
        self.viewer.camera.zoom = 1.0

    def _move_to_microscope(self):
        # TODO: fully implement this when have hardware
        _translation = {
            "x": 49.6167e-3,
            "y": -0.339e-3,
            "z": 0.137e-3,
        }  # TODO: move to config

        if self.microscope.fibsem_microscope is None:
            msg = f"Stage Movement is disabled (No OpenFIBSEM)"
            napari.utils.notifications.show_info(msg)
            logging.info(msg)
            return

        current_position_x = self.microscope.fibsem_microscope.get_stage_position().x

        fibsem_min = -10.0e-3
        fibsem_max = 10.0e-3
        lm_min = 40.0e-3
        lm_max = 60.0e-3

        x = _translation["x"]
        y = _translation["y"]
        z = _translation["z"]

        logging.info(f"Current position: {current_position_x}")
        msg: str
        if fibsem_min < current_position_x < fibsem_max:
            msg = "Under FIBSEM, moving to light microscope"
        elif lm_min < current_position_x < lm_max:
            x = -x
            y = -y
            z = -z
            msg = "Under light microscope, moving to FIBSEM"
        else:
            logging.warn(
                "Not positioned under the either microscope, cannot move to other microscope"
            )
            return

        logging.info(msg)
        napari.utils.notifications.show_info(msg)

        logging.info(f"Moving to microscope: x={x}, y={y}, z={z}")
        new_position = FibsemStagePosition(x=x, y=y, z=z, r=0, t=0)
        self.microscope.fibsem_microscope.move_stage_relative(new_position)

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

        if self.microscope.fibsem_microscope is None:
            msg = f"Stage Movement is disabled (No OpenFIBSEM): Coords: {coords[0]:.2f}, {coords[1]:.2f} "
            napari.utils.notifications.show_info(msg)
            logging.info(msg)
            return

        # image = self.image
        nominal_pixelsize = 6.5e-6 / 20  # / 2.94 # PATENTED_TECHNOLOGY
        pixelsize = 125e-6 / 350  # MEASURED

        # 6.5um/20px = 0.325 um/px
        # 125um/350px = 0.35714285714285715 um/px
        # 1/0.35714285714285715 = 2.8 px/um

        point = conversions.image_to_microscope_image_coordinates(
            Point(x=coords[1], y=coords[0]),
            image,
            pixelsize,
        )
        logging.info(f"IMAGE: {image.shape}, PIXELSIZE: {pixelsize:.2e}")

        logging.info(
            f"Movement: STABLE | COORD {coords} | SHIFT {point.x:.2e}, {point.y:.2e} | {beam_type}"
        )

        self.microscope.fibsem_microscope.stable_move(
            settings=self.microscope.fibsem_settings,
            dx=point.x,
            dy=point.y,
            beam_type=BeamType.ION,
        )

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

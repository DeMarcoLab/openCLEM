import os
from openlm import utils
from openlm import config
from openlm.structures import ImageMode, SynchroniserMessage, ImageSettings, DetectorSettings
import time
import logging
import numpy as np
from PIL import Image
from openlm.microscope import LightMicroscope

from dataclasses import dataclass
from openlm.structures import (LaserSettings, ImageMode, TriggerEdge, TriggerSource, 
    DetectorSettings, ObjectiveSettings, LightImage, LightImageMetadata)

def test_acq(microscope: LightMicroscope, mode: ImageMode = ImageMode.SINGLE):
    microscope._laser_controller.initialise() # TODO: move to init @DavidDierickx

    # time.sleep(3)
    # microscope.get_synchroniser().stop_sync()
    microscope.setup_acquisition()
    # mode = mode

    sync_message = SynchroniserMessage(
        exposures= [1000, 0, 1000, 1000],
        pins=  {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
        mode=mode,
        n_slices = 4,
        trigger_edge = TriggerEdge.RISING,
    )

    image_settings = ImageSettings(
        pixel_size=25e-6,
        exposure=500.e-3,
        n_images = 4,
        mode=mode,
    )

    image_settings.n_images = len([v for v in sync_message.exposures if v > 0])

    image_queue, stop_event = microscope.acquire_image(
        image_settings=image_settings, 
        sync_message=sync_message)

    time.sleep(1) # wait for camera to start?

    microscope.consume_image_queue()

import numpy as np
import itertools
from pprint import pprint

def _gen_tiling_workflow(n_rows=1, n_cols=1, dx=0, dy=0):
    """Generator for tile indices"""    
    moves = [[j*dx, i*dy] for i in range(n_rows) for j in range(n_cols)]
    return moves

def _gen_volume_workflow(n_slices, dz):
    if n_slices % 2 == 0:
        n_slices += 1
        print("Must be odd atm, adding 1")

    list_ = list(np.linspace(-(n_slices-1)//2, n_slices//2, n_slices)*dz)
    return list_[::-1]

# check the difference in each element of the list compared to the previous element
# if the difference is 0, then the stage is not moving
from copy import deepcopy


def _gen_workflow(tile_coords:list, 
                  volume_coords:list,
                  image_settings:ImageSettings,
                  sync_message:SynchroniserMessage,
                  return_to_origin: bool = True 
                  ) -> list[dict]:
    workflow = []

    current_position = [0, 0, 0]

    for tile_coord in tile_coords:
        dx = tile_coord[0] - current_position[0]
        dy = -(tile_coord[1] - current_position[1])

        if not(dx == 0 and dy == 0):
            # print(f"Tile moves by dx={dx}, dy={dy}")
            workflow.append({"type": "move_stage", "dx": dx, "dy": dy})

        current_position[0] = tile_coord[0]
        current_position[1] = tile_coord[1]

        for volume_coord in volume_coords:
            dz = volume_coord - current_position[2]
            if not (dz == 0):
                workflow.append({"type": "move_objective", "dz": dz})
            current_position[2] = volume_coord

            ## REPLACE THIS WITH IMAGE DAT ## 
            workflow.append({"type": "acquire_image", 
                             "sync": deepcopy(sync_message), 
                             "settings": deepcopy(image_settings), 
                             "stop_event": None})

    if return_to_origin:
        # move back to begining
        dx = -current_position[0]
        dy = current_position[1]
        dz = -current_position[2]
        if not (dx == 0 and dy == 0):
            workflow.append({"type": "move_stage", "dx": dx, "dy": dy})
        if not (dz == 0):
            workflow.append({"type": "move_objective", "dz": dz})

    return workflow

from openlm.structures import WorkflowSettings
def generate_workflow(workflow_settings: WorkflowSettings, image_settings: ImageSettings, sync_message: SynchroniserMessage):
    """Generate a workflow based on the workflow settings"""
    tile_coords = _gen_tiling_workflow(workflow_settings.n_rows, workflow_settings.n_cols, workflow_settings.dx, workflow_settings.dy)
    volume_coords = _gen_volume_workflow(workflow_settings.n_slices, workflow_settings.dz)
    workflow = _gen_workflow(tile_coords, volume_coords, image_settings, sync_message, return_to_origin=workflow_settings.return_to_origin)
    return workflow





################### v2 #####################

from dataclasses import dataclass

from openlm.microscope import LightMicroscope
from abc import ABC, abstractmethod

@dataclass
class OpenLMWorkflowStep(ABC):
    type: str
    name: str
    params: dict

    @abstractmethod
    def run(self, microscope: LightMicroscope, return_fn=None, *args, **kwargs):
        pass

class OpenLMWorkflowStepMoveStage(OpenLMWorkflowStep):
    def __init__(self, name: str, params: dict):
        super().__init__(type="move_stage", name=name, params=params)

    def run(self,microscope: LightMicroscope, return_fn=None):
        worker = microscope.move_stage(dx=self.params["dx"], dy=self.params["dy"])
        worker.returned.connect(return_fn)  # type: ignore
        worker.start()

class OpenLMWorkflowStepAcquireImage(OpenLMWorkflowStep):
    def __init__(self, name: str, params: dict):
        super().__init__(type="acquire_image", name=name, params=params)

    def run(self, microscope: LightMicroscope, return_fn=None ):
        self.params["parent_ui"].stop_event.clear()
        microscope.setup_acquisition()

        # TODO: disable other microscope interactions
        worker = microscope.consume_image_queue(save=True, parent_ui=self.params["parent_ui"])
        worker.returned.connect(return_fn)  # type: ignore
        worker.start()

        time.sleep(1)

        # acquire image
        self.params["parent_ui"].image_queue, self.params["parent_ui"].stop_event = microscope.acquire_image(
            image_settings=self.params["settings"],
            sync_message=self.params["sync"],
            stop_event=self.params["parent_ui"].stop_event,
        )

class OpenLMWorkflowStepMoveObjective(OpenLMWorkflowStep):
    def __init__(self, name: str, params: dict):
        super().__init__(type="move_objective", name=name, params=params)

    def run(self, microscope: LightMicroscope, return_fn=None, ):
        logging.info(f"Objective Move: {self.params['dz']}")
        worker = microscope.move_objective_stage(dz=self.params["dz"])
        worker.returned.connect(return_fn)  # type: ignore
        worker.start()

from typing import Callable

def _gen_workflow_v2(tile_coords:list, 
                  volume_coords:list,
                  image_settings:ImageSettings,
                  sync_message:SynchroniserMessage,
                  return_to_origin: bool = True, 
                  ) -> list[OpenLMWorkflowStep]:
    workflow = []

    current_position = [0, 0, 0]

    for tile_coord in tile_coords:
        dx = tile_coord[0] - current_position[0]
        dy = -(tile_coord[1] - current_position[1])

        if not(dx == 0 and dy == 0):
            workflow.append(OpenLMWorkflowStepMoveStage(name="move_stage", params={"dx": dx, "dy": dy}))

        current_position[0] = tile_coord[0]
        current_position[1] = tile_coord[1]

        for volume_coord in volume_coords:
            dz = volume_coord - current_position[2]
            if not (dz == 0):
                workflow.append(OpenLMWorkflowStepMoveObjective(name="move_objective", params={"dz": dz}))
            current_position[2] = volume_coord

            ## REPLACE THIS WITH IMAGE DAT ## 
            workflow.append(OpenLMWorkflowStepAcquireImage(name="acquire_image", params={"sync": deepcopy(sync_message), 
                                "settings": deepcopy(image_settings), 
                                "stop_event": None}))

    if return_to_origin:
        # move back to begining
        dx = -current_position[0]
        dy = current_position[1]
        dz = -current_position[2]
        if not (dx == 0 and dy == 0):
            workflow.append(OpenLMWorkflowStepMoveStage(name="move_stage", params={"dx": dx, "dy": dy}))
        if not (dz == 0):
            workflow.append(OpenLMWorkflowStepMoveObjective(name="move_objective", params={"dz": dz}))

    return workflow


def generate_workflow_v2(workflow_settings: WorkflowSettings, image_settings: ImageSettings, sync_message: SynchroniserMessage):
    """Generate a workflow based on the workflow settings"""
    tile_coords = _gen_tiling_workflow(workflow_settings.n_rows, workflow_settings.n_cols, workflow_settings.dx, workflow_settings.dy)
    volume_coords = _gen_volume_workflow(workflow_settings.n_slices, workflow_settings.dz)
    workflow = _gen_workflow_v2(tile_coords, volume_coords, image_settings, sync_message, return_to_origin=workflow_settings.return_to_origin)
    return workflow
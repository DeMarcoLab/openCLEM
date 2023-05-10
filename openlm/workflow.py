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
        # print("--"*20)

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
    workflow = _gen_workflow(tile_coords, volume_coords, image_settings, sync_message)
    return workflow







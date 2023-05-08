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



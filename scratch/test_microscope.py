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
from openlm.workflow import test_acq

# cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc.yaml")
cfg = utils.load_yaml(cfg_path)
microscope, settings = utils.setup_session(config_path=cfg_path)


test_acq(microscope, mode=ImageMode.SINGLE)


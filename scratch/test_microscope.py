import os
from openclem import utils
from openclem import config
from openclem.structures import SynchroniserMessage, ImageSettings, DetectorSettings
import time

# cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc.yaml")
cfg = utils.load_yaml(cfg_path)
microscope, settings = utils.setup_session(config_path=cfg_path)

microscope.acquire_image(image_settings=None)



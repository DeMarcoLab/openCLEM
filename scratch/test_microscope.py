import os
from openclem import utils
from openclem import config
from openclem.structures import SynchroniserMessage, ImageSettings, DetectorSettings
import time

# cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc.yaml")
cfg = utils.load_yaml(cfg_path)
microscope, settings = utils.setup_session(config_path=cfg_path)

microscope._objective.relative_move(int(2.01e6))

# microscope.setup_acquisition()

# # Set up sync
# synchroniser_message = SynchroniserMessage.__from_dict__({
#     "exposures": [1000, 1000, 1000, 1000],
#     "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
#     "mode": "live",
#     "n_slices": 4,
#     "trigger_edge": "RISING",
# })

# image_settings = ImageSettings(
#     pixel_size=25e-6,
#     exposure=0.1,
#     n_images = 12,
# )

# microscope.acquire_image(image_settings=image_settings, 
#                          sync_message=synchroniser_message)



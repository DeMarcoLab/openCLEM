import os
from openclem import utils
from openclem import config
from openclem.structures import ImageMode, SynchroniserMessage, ImageSettings, DetectorSettings
import time
import logging
import numpy as np
from PIL import Image

cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
# cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc.yaml")
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
microscope.setup_acquisition()
mode = ImageMode.LIVE

# Set up sync
synchroniser_message = SynchroniserMessage.__from_dict__({
    "exposures": [1000, 1000, 1000, 1000],
    "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
    "mode": mode.value,
    "n_slices": 4,
    "trigger_edge": "RISING",
})

image_settings = ImageSettings(
    pixel_size=25e-6,
    exposure=1,
    n_images = 4,
    mode=mode,
)

image_queue, stop_event= microscope.acquire_image(image_settings=image_settings, 
                         sync_message=synchroniser_message)

# poll until keyboard interrupt
try:
    i = 0
    while True:
        image = image_queue.get()
        
        logging.info(
            f"Getting image {i} in queue: {image.shape}, {np.mean(image)}"
        )

        # save image with PIL
        image = Image.fromarray(image)
        image.save(f"image_{i:03d}.png") 

        # time.sleep(0.1)
        i += 1

except KeyboardInterrupt:
    stop_event.set()
    logging.info("Keyboard interrupt")
finally:
    logging.info("Thread stopped.")


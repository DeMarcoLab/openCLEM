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

# microscope._objective.relative_move(1e-3)
# print(microscope._objective.position)

microscope._laser_controller.initialise() # TODO: move to init @DavidDierickx

# time.sleep(3)
# microscope.get_synchroniser().stop_sync()
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
    exposure=500.e-3,
    n_images = 4,
    mode=mode,
)

image_queue, stop_event = microscope.acquire_image(
    image_settings=image_settings, 
    sync_message=synchroniser_message)

time.sleep(1) # wait for camera to start?

try:
    counter = 0
    while image_queue.qsize() > 0 or not stop_event.is_set():
        image = image_queue.get()
        
        logging.info(f"Getting img {counter%4} in queue: {image.shape}, {np.mean(image)}"
        )

        # if False:
            # yield (image, f"Channel {counter % 4:02d}")
        counter += 1

except KeyboardInterrupt:
    stop_event.set()
    logging.info("Keyboard interrupt")
except Exception as e:
    stop_event.set()
    logging.error(e)
finally:
    microscope.get_synchroniser().stop_sync()
    logging.info("Thread stopped.")

# print("HELLO WORLD")
# logging.info("Consuming image")
microscope.consume_image()

# print("HELLO WORLD")

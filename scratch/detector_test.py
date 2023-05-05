import os
from openlm import utils
from openlm import config
from openlm.structures import SynchroniserMessage, ImageSettings, DetectorSettings
import time
import matplotlib.pyplot as plt

# set matplotlib backend
plt.switch_backend("Qt5Agg")

# cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc_copy.yaml")
cfg = utils.load_yaml(cfg_path)
microscope, settings = utils.setup_session(config_path=cfg_path)

# Set up detector
microscope._detector.init_camera()

image_settings = ImageSettings(
    pixel_size=25e-6,
    exposure=0.1,
)
# image = microscope._detector.grab_image(image_settings)
# print(image)
# print(image.shape)

# import numpy as np
# np.save("image.npy", image)

import logging

def _threaded_grab_image(microscope, image_settings, stop_event):
    
    while not stop_event.is_set():
        image = microscope._detector.grab_image(image_settings)
        logging.info("Image grabbed: " + str(image.shape))
        time.sleep(0.1)
    

import threading

stop_event = threading.Event()

_thread = threading.Thread(
    target=_threaded_grab_image, 
    args=(microscope, image_settings, stop_event)

)
_thread.start()

# poll until keyboard interrupt
try:
    while True:
        time.sleep(0.5)
        logging.info(f"Thread alive: {_thread.is_alive()}")
except KeyboardInterrupt:
    stop_event.set()
    logging.info("Keyboard interrupt")

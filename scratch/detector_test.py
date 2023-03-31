import os
from openclem import utils
from openclem import config
from openclem.structures import SynchroniserMessage, ImageSettings, DetectorSettings
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
image = microscope._detector.grab_image(image_settings)
print(image)
print(image.shape)

import numpy as np
np.save("image.npy", image)

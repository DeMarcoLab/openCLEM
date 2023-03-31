import os
from openclem import utils
from openclem import config
from openclem.structures import SynchroniserMessage, ImageSettings, DetectorSettings
import time

# cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc.yaml")
cfg = utils.load_yaml(cfg_path)
microscope, settings = utils.setup_session(config_path=cfg_path)

# Set up lasers
for laser in microscope._laser_controller.lasers:
    microscope._laser_controller.set_power(laser, 4.0)
# TODO: add in laser_settings for hardware triggering

# Set up detector



# Set up sync
synchroniser_message = SynchroniserMessage.__from_dict__({
    "exposures": [0, 0, 1000, 0],
    "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
    "mode": "single",
    "n_slices": 3,
    "trigger_edge": "RISING",
})

# Run sync
microscope.get_synchroniser().sync_image(synchroniser_message)



# objective =microscope._objective
# objective.relative_move(int(-0.02e6))

# for laser in microscope._laser_controller.lasers:
#     microscope._laser_controller.set_power(laser, 4.0)
#     print(microscope._laser_controller.get_power(laser))


# message = microscope._synchroniser.sync_image(synchroniser_message)
# time.sleep(1)
# synchroniser_message = SynchroniserMessage.__from_dict__({
#     "exposures": [100, 5000, 0, 0],
#     "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
#     "mode": "single",
#     "n_slices": 3,
#     "trigger_edge": "RISING",
# })
# message = microscope._synchroniser.sync_image(synchroniser_message)

# synchroniser_message = SynchroniserMessage.__from_dict__({
#     "exposures": [100, 1000, 0, 0],
#     "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
#     "mode": "single",
#     "n_slices": 3,
#     "trigger_edge": "RISING",
# })
# message = microscope._synchroniser.sync_image(synchroniser_message)


# microscope._detector.init_camera()
# image_settings = ImageSettings(
#     pixel_size=25e-6,
#     exposure=0.1,
# )
# image = microscope._detector.grab_image(image_settings)
# print(image)
# import matplotlib.pyplot as plt
# plt.imshow(image, cmap="gray")
# plt.show()
import os
from openclem import utils
from openclem import config
from openclem.structures import SynchroniserMessage, ImageSettings, DetectorSettings
import time

cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
cfg = utils.load_yaml(cfg_path)
laser_controller, detector, objective, synchroniser = utils.setup_session(config_path=cfg_path, online=True)

for laser in laser_controller.lasers:
    print(laser_controller.get_power(laser))
    laser_controller.set_power(laser, 2.0)
    print(laser_controller.get_power(laser))

synchroniser_message = SynchroniserMessage.__from_dict__({
    "exposures": [100, 1000, 0, 0],
    "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
    "mode": "single",
    "n_slices": 3,
    "trigger_edge": "RISING",
})
message = synchroniser.sync_image(synchroniser_message)
time.sleep(1)
synchroniser_message = SynchroniserMessage.__from_dict__({
    "exposures": [100, 5000, 0, 0],
    "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
    "mode": "single",
    "n_slices": 3,
    "trigger_edge": "RISING",
})
message = synchroniser.sync_image(synchroniser_message)

synchroniser_message = SynchroniserMessage.__from_dict__({
    "exposures": [100, 1000, 0, 0],
    "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
    "mode": "single",
    "n_slices": 3,
    "trigger_edge": "RISING",
})
message = synchroniser.sync_image(synchroniser_message)

# print(detector)
# print(detector.camera)

# image = detector.grab_image(detector.settings)
# # print(image)
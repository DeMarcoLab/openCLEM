import os
import time

# get path of openclem

from openclem import utils
from openclem.structures import MicroscopeSettings, ImageSettings
from openclem import config as cfg

import logging

def main():

    utils.configure_logging(cfg.LOG_PATH)

    config_path = os.path.join(cfg.BASE_PATH, "microscopes/config.yml")

    system_config = utils.load_yaml(config_path)
    microscope_settings = MicroscopeSettings.__from_dict__(
        system_config.get("microscope")
    )

    laser_controller_name = microscope_settings.laser_controller.name
    detector_name = microscope_settings.detector.name

    laser_controller, detector = utils.get_hardware_from_config(
        microscope_settings=microscope_settings
    )

    laser_controller.connect()
    laser_controller.set_power("laser_2", 2)
    laser_controller.lasers["laser_2"].emission_on()
    time.sleep(2)
    laser_controller.lasers["laser_2"].emission_off()

    image_settings = ImageSettings(
        pixel_size=6.5e-6,
        exposure=0.1,
        n_images=1,
    )

    detector.connect()
    detector.init_camera()
    detector.open_camera()
    images = detector.grab_image(image_settings=image_settings)

    print(images[0])


if __name__ == "__main__":
    main()

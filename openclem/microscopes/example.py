import os
import time

# get path of openclem
import openclem
from openclem import utils
from openclem.detector import Detector
from openclem.laser import Laser, LaserController
from openclem.lasers.ldi.ldi import LdiLaser, LdiLaserController
from openclem.structures import LaserSettings, MicroscopeSettings, SerialSettings
from pprint import pprint

openclem_path = openclem.__path__[0]


if __name__ == "__main__":
    config_path = os.path.join(openclem_path, "microscopes/config.yml")

    system_config = utils.load_yaml(config_path)
    microscope_settings = MicroscopeSettings.__from_dict__(
        system_config.get("microscope")
    )

    laser_controller_name = microscope_settings.laser_controller.name
    detector_name = microscope_settings.detector.name

    laser_controller, detector = utils.get_hardware_from_config(
        microscope_settings=microscope_settings
    )

    print(f"laser_controller: {laser_controller}")
    print(f"detector: {detector}")


# for laser in system_config.get("lasers"):
#     laser_settings = LaserSettings.__from_dict__(laser)
#     laser_controller.add_laser(LdiLaser(laser_settings=laser_settings, parent=laser_controller))


# # serial_settings = SerialSettings(serial_port='COM8',
# #                                  baudrate=9600,
# #                                  timeout=1)


# # laser_controller = LdiLaserController()
# # laser_controller.connect(serial_settings=serial_settings)
# # lasers = laser_controller.lasers

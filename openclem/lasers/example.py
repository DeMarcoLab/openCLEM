from openclem.structures import SerialSettings, LaserSettings, MicroscopeSettings
from openclem.laser import LaserController
from openclem.lasers.ldi.ldi import LdiLaserController, LdiLaser
import time
import os
from openclem import utils

# get path of openclem
import openclem
openclem_path = openclem.__path__[0]
config_path = os.path.join(openclem_path, 'microscopes/config.yml')

system_config = utils.load_yaml(config_path)

# get subclasses of LaserController
import inspect
from openclem.laser import LaserController
subclasses = inspect.getmembers(LaserController, inspect.isclass)

print(subclasses)




# microscope_settings = MicroscopeSettings.__from_dict__(system_config.get("microscope"))


# laser_controller = LdiLaserController()

# for laser in system_config.get("lasers"):
#     laser_settings = LaserSettings.__from_dict__(laser)
#     laser_controller.add_laser(LdiLaser(laser_settings=laser_settings, parent=laser_controller))



# # serial_settings = SerialSettings(serial_port='COM8', 
# #                                  baudrate=9600, 
# #                                  timeout=1)


# # laser_controller = LdiLaserController()
# # laser_controller.connect(serial_settings=serial_settings)
# # lasers = laser_controller.lasers

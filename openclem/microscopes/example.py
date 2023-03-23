import os
import time

# get path of openclem
import openclem
from openclem import utils
from openclem.structures import MicroscopeSettings, ImageSettings

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

    # print(laser_controller.lasers)

    # laser_controller.connect()
    # laser_controller.set_power("laser_2", -1)
    # print(laser_controller.get_power("laser_2"))
    # laser_controller.lasers["laser_2"].emission_on()
    # time.sleep(1)
    # laser_controller.lasers["laser_2"].emission_off()

    # laser_controller.set_power("laser_2", 3)
    # print(laser_controller.get_power("laser_2"))
    # laser_controller.lasers["laser_2"].emission_on()
    # time.sleep(1)
    # laser_controller.lasers["laser_2"].emission_off()

    image_settings = ImageSettings(pixel_size=6.5e-6, exposure=0.1, 
                                   image_format="tiff")


    detector.connect()
    detector.init_camera()
    detector.open_camera()
    image = detector.grab_image(image_settings=image_settings)

    print(image)
    # print(detector)
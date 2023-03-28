import os

BASE_PATH = __file__
BASE_PATH = os.path.dirname(BASE_PATH)
LOG_PATH = os.path.join(BASE_PATH, "log")

os.makedirs(LOG_PATH, exist_ok=True)


# structure is: {config_name: [folder_name.file_name, class_name]}
AVAILABLE_LASERS = {"demo": ["demo.demo", "DemoLaser"],
                    "89North_ldi_Laser": ["ldi.ldi", "LdiLaser"],
                    "Toptica_iCLE_Laser": ["iCLE.iCLE", "iCLELaser"]}

AVAILABLE_DETECTORS = {
    "demo": ["demo.demo", "DemoDetector"],
    "BasleracA1920_155um": ["basler.basler", "BasleracA1920_155um"],
    "hamamatsuOrcaFlash4": ["hamamatsu.hamamatsu", "HamamatsuOrcaFlash4"],
}

AVAILABLE_LASER_CONTROLLERS = {
    "demo": ["demo.demo", "DemoLaserController"],
    "Toptica_iCLE": ["iCLE.iCLE", "iCLELaserController"],
    "89North_ldi": ["ldi.ldi", "LdiLaserController"],
}

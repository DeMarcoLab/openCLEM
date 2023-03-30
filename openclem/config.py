import os

CONFIG_PATH = __file__
BASE_PATH = os.path.dirname(CONFIG_PATH)
LOG_PATH = os.path.join(BASE_PATH, "log")

os.makedirs(LOG_PATH, exist_ok=True)


# structure is: {config_name: [folder_name.file_name, class_name]}
AVAILABLE_LASERS = {"demo": ["demo.demo", "DemoLaser"],
                    "89North_ldi_Laser": ["89north.ldi", "LdiLaser"],
                    "Toptica_iCLE_Laser": ["toptica.iCLE", "iCLELaser"]}

AVAILABLE_DETECTORS = {
    "demo": ["demo.demo", "DemoDetector"],
    "BasleracA1920_155um": ["basler.basler", "BasleracA1920_155um"],
    "hamamatsuOrcaFlash4": ["hamamatsu.hamamatsu", "HamamatsuOrcaFlash4"],
}

AVAILABLE_LASER_CONTROLLERS = {
    "demo": ["demo.demo", "DemoLaserController"],
    "Toptica_iCLE": ["toptica.iCLE", "iCLELaserController"],
    "89North_ldi": ["89north.ldi", "LdiLaserController"],
}

AVAILABLE_OBJECTIVES = {
    "demo": ["demo.demo", "DemoObjective"],
    "smaract": ["smaract.SMARACT", "SMARACTObjectiveStage"],
}
import importlib
import logging
import os
import sys
from pathlib import Path

import serial
import serial.tools.list_ports
import yaml
import time
import datetime

from openclem.config import (
    AVAILABLE_DETECTORS,
    AVAILABLE_LASER_CONTROLLERS,
    AVAILABLE_LASERS,
    AVAILABLE_OBJECTIVE_STAGES,
)
from openclem.config import BASE_PATH, LOG_PATH
from openclem.structures import MicroscopeSettings, SerialSettings
from openclem.laser import Laser, LaserController
from openclem.detector import Detector
from openclem.microscope import LightMicroscope



def load_yaml(fname: Path) -> dict:
    """load yaml file

    Args:
        fname (Path): yaml file path

    Returns:
        dict: Items in yaml
    """
    with open(fname, "r") as f:
        config = yaml.safe_load(f)

    return config


def current_timestamp():
    """Returns current time in a specific string format

    Returns:
        String: Current time
    """
    return datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d-%I-%M-%S%p")


def setup_session(session_path: Path = None,
                  config_path: Path = None,
                  setup_logging: bool = True,
                  online: bool = True) -> tuple[LightMicroscope, MicroscopeSettings]:

    settings = load_settings_from_config(config_path=config_path)

    cls_laser, cls_laser_controller, cls_detector, cls_objective_stage = import_hardware_modules(settings)

    session = f'{settings.name}_{current_timestamp()}'

        # configure paths
    if session_path is None:
        session_path = os.path.join(LOG_PATH, session)
    os.makedirs(session_path, exist_ok=True)

    # configure logging
    if setup_logging:
        configure_logging(path=session_path, log_level=logging.DEBUG)

    laser_controller = cls_laser_controller(settings.laser_controller)
    detector = cls_detector(settings.detector)
    for laser_ in settings.lasers:
        laser = cls_laser(laser_, parent=laser_controller)
        laser_controller.add_laser(laser)

    objective_stage = cls_objective_stage(settings.objective_stage.name)
    
    if online:
        laser_controller.connect()
        detector.connect()
    
    return [laser_controller, detector, objective_stage]


def load_settings_from_config(config_path: Path = None) -> MicroscopeSettings:
    if config_path is None:
        config_path = os.path.join(BASE_PATH, "config", "system.yaml")

    config = load_yaml(config_path)
    microscope_settings = MicroscopeSettings.__from_dict__(config)
    return microscope_settings


def import_hardware_modules(microscope_settings: MicroscopeSettings) -> tuple[Laser, LaserController, Detector]:
    # structure is {hardware_type: [hardware_folder_name, hardware_name, availability_dict]}
    hardware_dict = {
        "laser": [
            "lasers",
            microscope_settings.laser_controller.laser,
            AVAILABLE_LASERS,
        ],
        "laser_controller": [
            "lasers",
            microscope_settings.laser_controller.name,
            AVAILABLE_LASER_CONTROLLERS,
        ],
        "detector": [
            "detectors",
            microscope_settings.detector.name,
            AVAILABLE_DETECTORS,
        ],
        "objective_stage": [
            "objective_stages",
            microscope_settings.objective_stage.name,
            AVAILABLE_OBJECTIVE_STAGES,
        ],
    }

    classes = []

    for hardware_type in hardware_dict:
        hardware_type_str = hardware_dict[hardware_type][0]
        hardware_name = hardware_dict[hardware_type][1]
        availablility_dict = hardware_dict[hardware_type][2]

        if hardware_name not in availablility_dict:
            raise ValueError(f"Hardware {hardware_name} not available")

        module_name = (
            f"openclem.{hardware_type_str}.{availablility_dict[hardware_name][0]}"
        )

        module = importlib.import_module(module_name)
        cls = getattr(module, availablility_dict[hardware_name][1])
        classes.append(cls)
        logging.info(f"imported {hardware_type} {cls}")
        print(os.path.dirname(module.__file__))

    return classes

# TODO: better logs: https://www.toptal.com/python/in-depth-python-logging
# https://stackoverflow.com/questions/61483056/save-logging-debug-and-show-only-logging-info-python
def configure_logging(path: Path = "", log_filename="logfile", log_level=logging.DEBUG):
    """Log to the terminal and to file simultaneously."""
    logfile = os.path.join(path, f"{log_filename}.log")

    file_handler = logging.FileHandler(logfile)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)

    logging.basicConfig(
        format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
        level=log_level,
        handlers=[file_handler, stream_handler],
        force=True,
    )

    return logfile

from openclem.microscopes.base import BaseLightMicroscope
def create_microscope(name, det, lc, obj) -> BaseLightMicroscope:

    lm = BaseLightMicroscope(name=name)
    lm.add_detector(det)
    lm.add_objective(obj)
    lm.add_laser_controller(lc)

    lm.connect()

    return lm
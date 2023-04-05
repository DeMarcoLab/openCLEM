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
    AVAILABLE_OBJECTIVES,
    AVAILABLE_SYNCHRONISERS,
)
from openclem.config import BASE_PATH, LOG_PATH
from openclem.structures import MicroscopeSettings, SerialSettings
from openclem.laser import Laser, LaserController
from openclem.detector import Detector
from openclem.microscope import LightMicroscope
from openclem.microscopes.base import BaseLightMicroscope
from openclem.objective import ObjectiveStage
from openclem.synchronisation import Synchroniser


def write_serial_command(port: serial.Serial, command, check=True):
    """Send a command to a serial port and return the response
       Expects a newline character at the end of the response
       Expects the port to be opened before calling

    Args:
        port (serial.Serial): _description_
        command (_type_): _description_
        check (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    if not port.is_open:
        port.open()
    port.write(bytes(command, "utf-8"))
    if check:
        response = port.readline()
        return response
    return None


def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return ports


def get_port_names(ports):
    port_names = [port.device for port in ports]
    return port_names


def connect_to_serial_port(serial_settings: SerialSettings):
    port_name = serial_settings.port
    baudrate = serial_settings.baudrate
    timeout = serial_settings.timeout

    serial_connection = serial.Serial(
        port=port_name, baudrate=baudrate, timeout=timeout
    )
    return serial_connection


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

    # datetime as string with microseconds
    return datetime.datetime.now().strftime("%Y-%m-%d-%I-%M-%S-%f%p")

    # return datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d-%I-%M-%S%p")


def setup_session(
    session_path: Path = None,
    config_path: Path = None,
    setup_logging: bool = True,
) -> tuple[LightMicroscope, MicroscopeSettings]:
    settings = load_settings_from_config(config_path=config_path)
    session = f"{settings.name}_{current_timestamp()}"

    # configure paths
    if session_path is None:
        session_path = os.path.join(LOG_PATH, session)
    os.makedirs(session_path, exist_ok=True)

    # configure logging
    if setup_logging:
        configure_logging(path=session_path, log_level=logging.DEBUG)

    (
        cls_laser,
        cls_laser_controller,
        cls_detector,
        cls_objective,
        cls_synchroniser,
    ) = import_hardware_modules(settings)

    # if online:
    laser_controller = cls_laser_controller(settings.laser_controller)
    detector = cls_detector(settings.detector)
    objective = cls_objective(settings.objective_stage)
    synchroniser = cls_synchroniser(settings.synchroniser)

    for laser_ in settings.lasers:
        laser = cls_laser(laser_, parent=laser_controller)
        laser_controller.add_laser(laser)

    # create microscope
    microscope = create_microscope(
        name=settings.name,
        det=detector,
        lc=laser_controller,
        obj=objective,
        synchroniser=synchroniser,
        online=settings.online
    )

    return microscope, settings


def load_settings_from_config(config_path: Path = None) -> MicroscopeSettings:
    if config_path is None:
        config_path = os.path.join(BASE_PATH, "config", "system.yaml")

    config = load_yaml(config_path)
    microscope_settings = MicroscopeSettings.__from_dict__(config)
    return microscope_settings


def import_hardware_modules(
    microscope_settings: MicroscopeSettings,
) -> tuple[Laser, LaserController, Detector]:
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
        "objectives": [
            "objectives",
            microscope_settings.objective_stage.name,
            AVAILABLE_OBJECTIVES,
        ],
        "synchronisers": [
            "synchronisers",
            microscope_settings.synchroniser.name,
            AVAILABLE_SYNCHRONISERS,
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


def create_microscope(
    name: str,
    det: Detector,
    lc: LaserController,
    obj: ObjectiveStage,
    synchroniser: Synchroniser,
    online: bool = True,
) -> BaseLightMicroscope:
    lm = BaseLightMicroscope(name=name)
    lm.add_detector(det)
    lm.add_objective(obj)
    lm.add_laser_controller(lc)
    lm.add_synchroniser(synchroniser)
    if online:
        lm.connect()
        lm.initialise()

    for laser in lm.get_laser_controller().lasers:
        lm.get_laser_controller().set_power(laser, 0)
        # TODO: set laser power properly

    return lm

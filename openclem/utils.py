import glob
import importlib
import inspect
import logging
import os
from pathlib import Path

import serial
import serial.tools.list_ports
import yaml

import openclem
from openclem.detector import Detector
from openclem.laser import LaserController, Laser
from openclem.structures import SerialSettings, MicroscopeSettings

IGNORED_MODULES = ["__init__", "template"]
openclem_path = openclem.__path__[0]
BASENAME = os.path.basename(openclem_path)


def write_serial_command(port: serial.Serial, command):
    port.close()
    port.open()
    port.write(bytes(command, "utf-8"))
    response = port.read_until(expected=b"\r")
    port.close()
    return response


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


def get_subclass(cls, path: str) -> list:
    package_path = os.path.join(BASENAME, path)
    # get all modules in package path
    module_names = [
        os.path.splitext(os.path.abspath(f))[0]
        for f in glob.glob(os.path.join(package_path, "**/**.py"), recursive=False)
    ]

    # clean up ignored modules such as __init__
    module_names = [
        module
        for module in module_names
        if not any([a in module for a in IGNORED_MODULES])
    ]

    # turn string for module path into importable module name
    module_names = [
        module.replace(os.path.abspath(package_path), "").replace("\\", ".")
        for module in module_names
    ]
    import_base = f"{BASENAME}.{path}"
    module_names = [f"{import_base}{module}" for module in module_names]

    # import modules found
    for module_ in module_names:
        try:
            importlib.import_module(module_)
        except Exception as e:
            logging.error(f"Error importing module {module_}: {e}")

    subclasses = cls.__subclasses__()
    return subclasses


def get_subclasses():
    # get availablable hardware
    laser_controllers = get_subclass(cls=LaserController, path="lasers")
    lasers = get_subclass(cls=Laser, path="lasers")
    detectors = get_subclass(cls=Detector, path="detectors")
    return laser_controllers, detectors, lasers


def get_hardware_from_config(microscope_settings: MicroscopeSettings) -> tuple[LaserController, Detector]:
    available_laser_controllers, available_detectors, available_lasers = get_subclasses()
    laser_controller_name = microscope_settings.laser_controller.name
    detector_name = microscope_settings.detector.name
    laser_name = microscope_settings.laser_controller.laser_type
    # these are factory methods, improve implementation
    for subclass in available_laser_controllers:
        if laser_controller_name == subclass.__id__():
            laser_controller = subclass(microscope_settings.laser_controller)
    for subclass in available_detectors:
        if detector_name == subclass.__id__():
            detector = subclass(microscope_settings.detector)
    for subclass in available_lasers:
        if laser_name == subclass.__id__():
            for laser in microscope_settings.lasers:
                laser_controller.add_laser(subclass(laser_settings=laser, parent=laser_controller))

    return laser_controller, detector

import sys

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

from openclem import config as cfg

def setup_hardware(path: Path = None):

    configure_logging(cfg.LOG_PATH)
    if path is None:
        path = os.path.join(cfg.BASE_PATH, "microscopes/config.yml")

    system_config = load_yaml(path)
    microscope_settings = MicroscopeSettings.__from_dict__(
        system_config.get("microscope")
    )

    laser_controller, detector = get_hardware_from_config(
        microscope_settings=microscope_settings
    )

    detector.connect()
    detector.init_camera()
    laser_controller.connect()

    return laser_controller, detector
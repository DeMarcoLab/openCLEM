import importlib
import logging
import os
import sys
from pathlib import Path

import serial
import serial.tools.list_ports
import yaml

from openclem.config import (
    AVAILABLE_DETECTORS,
    AVAILABLE_LASER_CONTROLLERS,
    AVAILABLE_LASERS,
)
from openclem.structures import MicroscopeSettings, SerialSettings


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


def import_hardware_modules(microscope_settings: MicroscopeSettings) -> None:
    # structure is {hardware_type: [hardware_folder_name, hardware_name, availability_dict]}
    hardware_dict = {
        "laser": [
            "lasers",
            microscope_settings.laser_controller.laser_type,
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
    }

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
        logging.info(f"imported {hardware_type} {cls}")
        print(f"imported {hardware_type} {cls}")


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

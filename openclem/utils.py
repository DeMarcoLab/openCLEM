import glob
import inspect
import os
from pathlib import Path

import serial
import serial.tools.list_ports
import yaml

import importlib
from openclem.structures import SerialSettings

IGNORED_MODULES = ["__init__", "template"]


def write_serial_command(serial_port: serial.Serial, command):
    serial_port.close()
    serial_port.open()
    serial_port.write(bytes(command, 'utf-8'))
    response = serial_port.read_until(expected=b'\r')
    serial_port.close()
    return response

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return ports

def get_port_names(ports):
    port_names = [port.device for port in ports]
    return port_names

def connect_to_serial_port(serial_settings: SerialSettings):
    port_name = serial_settings.serial_port
    baudrate = serial_settings.baudrate
    timeout = serial_settings.timeout
    
    serial_connection = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
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

def get_subclasses(cls, path):
    module_names = [
        os.path.splitext(os.path.abspath(f))[0]
        for f in glob.glob(os.path.join(path, "**/**.py"))
    ]

    module_names = [
        module
        for module in module_names
        if not any([a in module for a in IGNORED_MODULES])
    ]

    module_names = [module.replace(os.path.abspath(path), "").replace("\\", ".") for module in module_names]
    # prepend path
    path = path.replace("/", ".")
    module_names = [f"{path}{module}" for module in module_names]
    for module_ in module_names:
            try: 
                importlib.import_module(module_)
            except Exception as e:
                print(e)
    return module_names

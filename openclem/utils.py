import glob
import inspect
import os
from pathlib import Path

import serial
import serial.tools.list_ports
import yaml

import importlib
from openclem.structures import SerialSettings
import openclem
import logging

IGNORED_MODULES = ["__init__", "template"]
openclem_path = openclem.__path__[0]
BASENAME = os.path.basename(openclem_path)

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

def get_subclasses(cls, path: str) -> list:

    package_path = os.path.join(BASENAME, path)
    print(f"Package path: {package_path}")
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
    module_names = [module.replace(os.path.abspath(package_path), "").replace("\\", ".") for module in module_names]
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

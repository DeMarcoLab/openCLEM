import logging

import numpy as np

from openclem import utils
from openclem.laser import Laser, LaserController
from openclem.structures import LaserControllerSettings, LaserSettings

class LdiLaserController(LaserController):
    def __init__(self, laser_controller_settings: LaserControllerSettings):
        self.settings = laser_controller_settings
        self._name = self.settings.name
        self._laser = self.settings.laser
        self.serial_connection = None
        self.lasers = {}

    @classmethod
    def __id__(self):
        return "ldi"

    @property
    def name(self):
        return self._name

    def add_laser(self, laser: Laser):
        self.lasers[laser.name] = laser

    def connect(self):
        self.serial_connection = utils.connect_to_serial_port(serial_settings=self.settings.serial_settings)

    def disconnect(self):
        if self.serial_connection is None: return
        self.serial_connection.close()
        self.serial_connection = None

    def get_laser(self, name: str) -> Laser:
        return self.lasers[name]

    def set_power(self, name: str, value: float) -> None:
        self.lasers[name].power = value

    def get_power(self, name: str) -> float:
        return self.lasers[name].power

    # TODO: determine whether there is a salient difference between idling/shutter closing
    def close_emission(self):
        for laser in self.lasers.values():
            laser.emission_off()

    def close_shutters(self):
        for laser in self.lasers.values():
            laser.disable()


class LdiLaser(Laser):
    def __init__(self, laser_settings: LaserSettings, parent: LaserController):
        self.settings = laser_settings
        self._name = laser_settings.name
        self._serial_id = laser_settings.serial_id
        self._wavelength = laser_settings.wavelength
        self._power = laser_settings.power
        self._exposure_time = laser_settings.exposure_time
        self._enabled = laser_settings.enabled
        self._parent = parent
        if self._enabled:
            self.enable()
        else:
            self.disable()
        self._colour = laser_settings.colour

    @classmethod
    def __id__(self):
        return "ldilaser"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def serial_id(self):
        return self._serial_id

    @serial_id.setter
    def serial_id(self, value):
        self._serial_id = value

    @property
    def power(self):
        if self._parent.serial_connection is None: return
        command = (f"SET?\r")
        response = utils.write_serial_command(self._parent.serial_connection, command)
        self._power = self.decode_power(response)
        return self._power

    @power.setter
    def power(self, value):
        if self._parent.serial_connection is None: return
        value = int(np.clip(value, 0.0, 100.0))
        command = (f"SET:{self.serial_id}={value}\r")
        response = utils.write_serial_command(self._parent.serial_connection, command)
        if not self.check_response(response):
            logging.error(f"Error setting power for {self.name}")

    @property
    def wavelength(self):
        return f'{self._wavelength}nm'

    @wavelength.setter
    def wavelength(self, value: float):
        self._wavelength = float(value)

    def emission_on(self):
        if self._parent.serial_connection is None: return
        self._parent.close_shutters()
        self.enable()
        command = (f"RUN!\r")
        response = utils.write_serial_command(self._parent.serial_connection, command)
        if not self.check_response(response):
            logging.error(f"Error turning on laser for {self.name}")

    def emission_off(self):
        if self._parent.serial_connection is None: return
        self.disable()

    def enable(self):
        if self._parent.serial_connection is None: return
        command = (f"SHUTTER:{self.serial_id}=OPEN\r")
        response = utils.write_serial_command(self._parent.serial_connection, command)
        if self.check_response(response):
            self._shutter_open = True
        else:
            logging.error(f"Error opening shutter for {self.name}")

    def disable(self):
        if self._parent.serial_connection is None: return
        command = (f"SHUTTER:{self.serial_id}=CLOSED\r")
        response = utils.write_serial_command(self._parent.serial_connection, command)
        if self.check_response(response):
            self._shutter_open = False
        else:
            logging.error(f"Error closing shutter for {self.name}")

    def decode_power(self, response: str):
        response = response.decode('utf-8')
        start = response.find(self.serial_id) + len(self.serial_id) + 1
        end = response.find(',', start)
        return float(response[start:end])

    def check_response(self, response):
        return response == b'ok\n' or response == b'ok\r' or response == b'ok\r\n'

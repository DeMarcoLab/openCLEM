import logging

import numpy as np

from openlm import utils
from openlm.laser import Laser, LaserController
from openlm.structures import LaserControllerSettings, LaserSettings


class DemoLaser(Laser):
    def __init__(self, laser_settings: LaserSettings, parent: LaserController):
        self._parent = parent
        self.settings = laser_settings
        self.apply_settings(self.settings)

    def get(self) -> LaserSettings:

        return LaserSettings(name=self.name, 
                                serial_id=self.serial_id, 
                                wavelength=self.wavelength, 
                                power=self.power,
                                exposure_time=self.exposure_time, 
                                enabled=self.enabled, 
                                color=self._color)
    
    def apply_settings(self, laser_settings: LaserSettings):
        self.name = laser_settings.name
        self.serial_id = laser_settings.serial_id
        self.wavelength = laser_settings.wavelength
        self.power = laser_settings.power
        self.exposure_time = laser_settings.exposure_time
        self.enabled = laser_settings.enabled
        self._color = laser_settings.color

    @classmethod
    def __id__(self):
        return "demolaser"

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
        return self._power

    @power.setter
    def power(self, value):
        self._power = value

    @property
    def wavelength(self):
        return self._wavelength

    @wavelength.setter
    def wavelength(self, value: float):
        self._wavelength = float(value)

    @property
    def exposure_time(self) -> float:
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, value: float) -> None:
        self._exposure_time = value

    def enabled(self) -> bool:
        return self._enabled

    def emission_on(self):
        logging.info(f"Emission on for {self.name}")

    def emission_off(self):
        logging.info(f"Emission off for {self.name}")

    def enable(self):
        logging.info(f"Enabling {self.name}")

    def disable(self):
        logging.info(f"Disabling {self.name}")

class DemoLaserController(LaserController):
    def __init__(self, laser_controller_settings: LaserControllerSettings):
        self.settings = laser_controller_settings
        self._name = self.settings.name
        self._laser = self.settings.laser
        self.connection = None
        self.lasers = {}

    def initialise(self):
        pass

    @classmethod
    def __id__(self):
        return "demo"

    @property
    def name(self):
        return self._name

    def add_laser(self, laser: Laser):
        self.lasers[laser.name] = laser

    def connect(self):
        logging.info(f"Connecting to {self.name}")
        self.connection = "SerialConnection"
        logging.info(f"Connected to {self.name}")

    def disconnect(self):
        if self.connection is None: return
        logging.info(f"Disconnecting from {self.name}")
        self.connection = None

    def get_laser(self, name: str) -> Laser:
        return self.lasers[name]

    def set_power(self, name: str, value: float) -> None:
        self.lasers[name].power = value

    def get_power(self, name: str) -> float:
        return self.lasers[name].power

    def close_emission(self):
        for laser in self.lasers.values():
            laser.emission_off()

    def close_shutters(self):
        for laser in self.lasers.values():
            laser.disable()


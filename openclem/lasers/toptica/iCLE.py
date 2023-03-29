from openclem.laser import LaserController, Laser
from openclem import utils
import numpy as np
from openclem.structures import LaserControllerSettings, LaserSettings



class iCLELaserController(LaserController):
    def __init__(self, laser_controller_settings: LaserControllerSettings):
        self.settings = laser_controller_settings
        self._name = self.settings.name
        self._laser = self.settings.laser
        self.serial_connection = None
        self.lasers = {}
    
    @classmethod
    def __id__(self):
        return "iCLE"
    
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

class iCLELaser(Laser):
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
        return "iCLElaser"

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
        pass

    @property
    def wavelength(self):
        return self._wavelength
    
    @wavelength.setter
    def wavelength(self, value):
        pass

    def emission_on(self):
        print('Emission on')

    def emission_off(self):
        print('Emission off')

    def enable(self):
        print('Enable')

    def disable(self):
        print('Disable')


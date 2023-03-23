from openclem.laser import LaserController, Laser
from openclem import utils
import numpy as np

class iCLE(LaserController):
    def __init__(self, wavelength):
        self._wavelength = wavelength
        self._power = 0.0
        self.serial_id = None

    @classmethod
    def __id__(self):
        return "iCLE"
    
    @property
    def power(self):
        return self._power
    
    @power.setter
    def power(self, value):
        value = np.clip(value, 0.0, 100.0)
        command = (
            "(param-set! '" + self.serial_id + ":level " + str(round(value, 2)) + ")\r"
        )
        utils.write_serial_command(self.serial_connection, command)
        self._power = value

    def emission_on(self):
        print('Emission on')
        
    def emission_off(self):
        print('Emission off')

    def enable(self):
        print('Enable')

    def disable(self):
        print('Disable')

class iCLELaser(Laser):
    pass
from openclem.laser import LaserController
from openclem.structures import Laser, SerialSettings
import numpy as np
from openclem import utils

class LdiLaserController(LaserController):
    def __init__(self):
        self.serial_connection = None
        self.lasers = [Laser(name='laser_1', serial_id='405', wavelength=405.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0]),
                       Laser(name='laser_2', serial_id='488', wavelength=488.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0]),
                       Laser(name='laser_3', serial_id='555', wavelength=561.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0]),
                       Laser(name='laser_4', serial_id='640', wavelength=640.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0])]

    def connect(self, serial_settings: SerialSettings):
        self.serial_connection = utils.connect_to_serial_port(serial_settings=serial_settings)

    def disconnect(self):
        if self.serial_connection is None: return
        self.serial_connection.close()
        self.serial_connection = None


    @property
    def power(self, value):
        if self.serial_connection is None: return

        command = ()
        utils.write_serial_command(self.serial_connection, command)
        return self._power

    @power.setter
    def power(self, value):
        if self.serial_connection is None: return
        value = np.clip(value, 0.0, 100.0)
        command = ()
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
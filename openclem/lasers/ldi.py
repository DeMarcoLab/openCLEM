from openclem.laser import LaserController, Laser
from openclem.structures import LaserSettings, SerialSettings
import numpy as np
from openclem import utils

class LdiLaser(Laser):
    def __init__(self, name: str, serial_id: str, wavelength: float, 
                 power: float, exposure_time: float, enabled: bool, 
                 colour: list, parent: LaserController):
        self._name = name
        self._serial_id = serial_id
        self._wavelength = wavelength
        self._power = power
        self._exposure_time = exposure_time
        self._enabled = enabled
        self._colour = colour
        self.parent = parent

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
        if self.parent.serial_connection is None: return
        command = (f"SET?\r")
        response = utils.write_serial_command(self.parent.serial_connection, command)
        self._power = self.decode_power(response)
        return self._power
    
    @power.setter
    def power(self, value):
        if self.parent.serial_connection is None: return
        value = int(np.clip(value, 0.0, 100.0))
        command = (f"SET:{self.serial_id}={value}\r")
        response = utils.write_serial_command(self.parent.serial_connection, command)
        if self.check_response(response):
            self._power = value
        else:
            raise ValueError(f"Error setting power for {self.name} to {value}")

    @property
    def wavelength(self):
        return f'{self._wavelength}nm'

    @wavelength.setter
    def wavelength(self, value: float):
        self._wavelength = float(value)

    def decode_power(self, response: str):
        response = response.decode('utf-8')
        start = response.find(self.serial_id) + len(self.serial_id) + 1
        end = response.find(',', start)
        return float(response[start:end])
    
    def check_response(self, response):
        return response == b'ok\n'

class LdiLaserController(LaserController):
    def __init__(self):
        self.serial_connection = None
        # TODO: move to config?
        self.lasers = [LdiLaser(name='laser_1', serial_id='405', wavelength=405.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0], parent=self),
                       LdiLaser(name='laser_2', serial_id='488', wavelength=488.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0], parent=self),
                       LdiLaser(name='laser_3', serial_id='555', wavelength=555.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0], parent=self),
                       LdiLaser(name='laser_4', serial_id='640', wavelength=640.0, power=0.0,
                            exposure_time=1.0, enabled=False, colour=[0, 0, 0], parent=self)]

    def connect(self, serial_settings: SerialSettings):
        self.serial_connection = utils.connect_to_serial_port(serial_settings=serial_settings)

    def disconnect(self):
        if self.serial_connection is None: return
        self.serial_connection.close()
        self.serial_connection = None

    def emission_on(self):
        print('Emission on')

    def emission_off(self):
        print('Emission off')

    def enable(self):
        print('Enable')

    def disable(self):
        print('Disable')


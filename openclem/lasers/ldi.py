from openclem.laser import Laser

class LdiLaser(Laser):
    def __init__(self, wavelength):
        self._wavelength = wavelength
        self._power = 0.0

    @property
    def power(self):
        return self._power
    
    @power.setter
    def power(self, value):
        if value > 100:
            raise ValueError('Power must be between 0 and 100')
        if value < 0:
            raise ValueError('Power must be between 0 and 100')
        self._power = value

    @property
    def wavelength(self):
        return self._wavelength

    def emission_on(self):
        print('Emission on')
        
    def emission_off(self):
        print('Emission off')

    def enable(self):
        print('Enable')

    def disable(self):
        print('Disable')
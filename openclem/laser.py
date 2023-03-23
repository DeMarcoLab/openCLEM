from abc import ABC, abstractmethod

class Laser(ABC):
    def __init__(self, wavelength):
        self._wavelength = wavelength

    @property
    @abstractmethod
    def power(self):
        pass

    @power.setter
    @abstractmethod
    def power(self, value):
        pass
    
    @property
    @abstractmethod
    def wavelength(self):
        pass

    @abstractmethod
    def emission_on(self):
        pass

    @abstractmethod
    def emission_off(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass

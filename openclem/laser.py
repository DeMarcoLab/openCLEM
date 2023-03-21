from abc import ABC, abstractmethod

class Laser(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def set_power(self, power):
        pass

    @abstractmethod
    def get_power(self):
        pass

    @abstractmethod
    def set_wavelength(self, wavelength):
        pass

    @abstractmethod
    def get_wavelength(self):
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

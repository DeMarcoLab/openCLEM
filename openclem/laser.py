from abc import ABC, abstractmethod
from openclem.structures import SerialSettings
                                
class Laser(ABC):
    
    @property
    @abstractmethod
    def power(self) -> float:
        pass

    @power.setter
    @abstractmethod
    def power(self, value: float) -> None:
        pass

    @property
    @abstractmethod
    def wavelength(self) -> float:
        pass

    @wavelength.setter
    @abstractmethod
    def wavelength(self, value: float) -> None:
        pass


class LaserController(ABC):
    def __init__(self):
        self.lasers = []
        self.serial_connection = None

    @abstractmethod
    def connect(self, serial_settings: SerialSettings) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def emission_on(self, laser: Laser) -> None:
        pass

    @abstractmethod
    def emission_off(self, laser: Laser) -> None:
        pass

    @abstractmethod
    def enable(self, laser: Laser) -> None:
        pass

    @abstractmethod
    def disable(self, laser: Laser) -> None:
        pass
        
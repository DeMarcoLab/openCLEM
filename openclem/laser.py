from abc import ABC, abstractmethod
from openclem.structures import Laser, SerialSettings

class LaserController(ABC):
    def __init__(self):
        self.lasers = [Laser]

    @abstractmethod
    def connect(self, serial_settings: SerialSettings) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @property
    @abstractmethod
    def power(self, laser: Laser) -> float:
        pass

    @property
    @abstractmethod
    def wavelength(self, laser: Laser) -> float:
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
                                        
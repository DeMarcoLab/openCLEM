from abc import ABC, abstractmethod
from openclem.structures import LaserControllerSettings
                                
class Laser(ABC):
    
    @classmethod
    @abstractmethod
    def __id__(self):
        """the string by which you will import from config"""
        pass

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

    @abstractmethod
    def emission_on(self) -> None:
        pass

    @abstractmethod
    def emission_off(self) -> None:
        pass

    @abstractmethod
    def enable(self) -> None:
        pass

    @abstractmethod
    def disable(self) -> None:
        pass
        

class LaserController(ABC):
    def __init__(self, laser_controller_settings: LaserControllerSettings):
        self.settings = laser_controller_settings
        self.lasers = []
        self.serial_connection = None

    @classmethod
    @abstractmethod
    def __id__(self):
        """the string by which you will import from config"""
        pass
    
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def add_laser(self, laser: Laser) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


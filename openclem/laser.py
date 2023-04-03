from abc import ABC, abstractmethod
from openclem.structures import LaserControllerSettings, LaserSettings
                                
class Laser(ABC):

    def __init__(self, laser_settings: LaserSettings, parent: 'LaserController'):

        self.settings = laser_settings
        self._parent = parent
        self.set(laser_settings)
    
    def set(self, settings: LaserSettings) -> None:
        self.power = settings.power
        self.wavelength = settings.wavelength
        self.exposure_time = settings.exposure_time
        self._name = settings.name
        self._serial_id = settings.serial_id
        self.colour = settings.colour
        if settings.enabled:
            self.enable()
        else:
            self.disable()

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

    @property
    @abstractmethod
    def exposure_time(self) -> float:
        return self._exposure_time

    @exposure_time.setter
    @abstractmethod
    def exposure_time(self, value: float) -> None:
        self._exposure_time = value

    @property
    @abstractmethod
    def enabled(self) -> bool:
        self._enabled
    
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

    def __repr__(self) -> str:
        return f"{self.name} - Laser"
        

class LaserController(ABC):
    def __init__(self, laser_controller_settings: LaserControllerSettings):
        self.settings = laser_controller_settings
        self.lasers = {}
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

    @abstractmethod
    def get_laser(self, name: str) -> Laser:
        pass

    @abstractmethod
    def set_power(self, name: str, value: float) -> None:
        pass

    @abstractmethod
    def get_power(self, name: str) -> float:
        pass
    
    def __repr__(self) -> str:
        return f"{self.name} - LaserController"

    def get_powers(self) -> dict:
        return {laser.name: laser.power for laser in self.lasers.values()}
    
    def get_wavelengths(self) -> dict:
        return {laser.name: laser.wavelength for laser in self.lasers.values()}
    
    def get_enabled(self) -> dict:
        return {laser.name: laser.enabled for laser in self.lasers.values()}
    
    def get_exposure_times(self) -> dict:
        return {laser.name: laser.exposure_time for laser in self.lasers.values()}
    
    @abstractmethod
    def initialise(self):
        pass
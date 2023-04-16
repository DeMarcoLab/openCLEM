from abc import ABC, abstractmethod
from openclem.structures import LaserControllerSettings, LaserSettings

class Laser(ABC):

    def __init__(self, laser_settings: LaserSettings, parent: 'LaserController'):

        self._parent = parent
        self.settings = laser_settings
        self.apply_settings(self.settings)

    def get(self) -> LaserSettings:

        return LaserSettings(name=self.name, 
                                serial_id=self.serial_id, 
                                wavelength=self.wavelength, 
                                power=self.power,
                                exposure_time=self.exposure_time, 
                                enabled=self.enabled, 
                                color=self._color)
    
    def apply_settings(self, laser_settings: LaserSettings):
        self.name = laser_settings.name
        self.serial_id = laser_settings.serial_id
        self.wavelength = laser_settings.wavelength
        self.power = laser_settings.power
        self.exposure_time = laser_settings.exposure_time
        self.enabled = laser_settings.enabled
        self._color = laser_settings.color

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
        self.connection = None

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
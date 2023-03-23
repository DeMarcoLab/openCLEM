from dataclasses import dataclass
from enum import Enum


# class TriggerEdge(Enum):
#     """Trigger edge"""

#     RISING = 1
#     FALLING = 2


# class ExposureMode(Enum):
#     """Exposure mode"""

#     TIMED = 1
#     TRIGGER_WIDTH = 2


@dataclass
class ImageSettings:
    """Image settings"""

    pixel_size: float = 0.0
    exposure: float = 0.0
    image_format: str = "tiff"


@dataclass
class SerialSettings:
    """Serial settings"""

    serial_port: str = None
    baudrate: int = 9600
    timeout: float = 0.1

    @staticmethod
    def __from_dict__(settings: dict) -> "SerialSettings":
        return SerialSettings(
            serial_port=settings["serial_port"],
            baudrate=settings["baudrate"],
            timeout=settings["timeout"],
        )

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "serial_port": self.serial_port,
            "baudrate": self.baudrate,
            "timeout": self.timeout,
        }

@dataclass
class LaserSettings:
    name: str
    serial_id: str
    wavelength: float
    power: float
    exposure_time: float  # s
    enabled: bool
    colour: list

    @staticmethod
    def __from_dict__(settings: dict) -> "LaserSettings":

        laser_settings = LaserSettings(
            name=settings["name"],
            serial_id=settings["serial_id"],
            wavelength=settings["wavelength"],
            power=settings["power"],
            exposure_time=settings["exposure_time"],
            enabled=False,
            colour=settings["colour"],
        )
        return laser_settings

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "ID": self.serial_id,
            "wavelength": self.wavelength,
            "power": self.power,
            "exposure_time": self.exposure_time,
            "colour": self.colour,
        }
    
@dataclass
class DetectorSettings:
    """Detector settings"""

    name: str
    pixel_size: float
    resolution: list[int]

    @staticmethod
    def __from_dict__(settings: dict) -> "DetectorSettings":
            
            detector_settings = DetectorSettings(
                name=settings["name"],
                pixel_size=settings["pixel_size"],
                resolution=settings["resolution"],
            )
            return detector_settings
    
    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "pixel_size": self.pixel_size,
            "resolution": self.resolution,
        }
    

@dataclass
class MicroscopeSettings:
    """Microscope settings"""

    name: str
    detector: DetectorSettings
    image_settings: ImageSettings
    serial_settings: SerialSettings
    lasers: list

    @staticmethod
    def __from_dict__(settings: dict) -> "MicroscopeSettings":

        microscope_settings = MicroscopeSettings(
            name=settings["name"],
            image_settings=ImageSettings.__from_dict__(settings["image_settings"]),
            serial_settings=SerialSettings.__from_dict__(settings["serial_settings"]),
            lasers=[LaserSettings.__from_dict__(laser) for laser in settings["lasers"]],
        )
        return microscope_settings

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "image_settings": ImageSettings.__to_dict__(self.image_settings),
            "serial_settings": SerialSettings.__to_dict__(self.serial_settings),
            "lasers": [LaserSettings.__to_dict__(laser) for laser in self.lasers],
        }
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
    def __to_dict__(settings: "SerialSettings") -> dict:
        return {
            "serial_port": settings.serial_port,
            "baudrate": settings.baudrate,
            "timeout": settings.timeout,
        }

@dataclass
class Laser:
    name: str
    serial_id: str
    wavelength: float
    power: float
    exposure_time: float  # s
    enabled: bool
    colour: list

    @staticmethod
    def __from_dict__(settings: dict) -> "Laser":

        laser = Laser(
            name=settings["name"],
            serial_id=settings["ID"],
            wavelength=settings["wavelength"],
            power=settings["power"],
            exposure_time=settings["exposure_time"],
            enabled=False,
            pin=settings["pin"],
            volume_enabled=settings["volume_enabled"],
            colour=settings["colour"],
            spinBox=None,
            lineEdit=None,
            volumeCheckBox=None,
        )
        return laser

    @staticmethod
    def __to_dict__(settings: "Laser") -> dict:
        return {
            "name": settings.name,
            "ID": settings.serial_id,
            "wavelength": settings.wavelength,
            "power": settings.power,
            "exposure_time": settings.exposure_time,
            "pin": settings.pin,
            "volume_enabled": settings.volume_enabled,
            "colour": settings.colour,
        }
    
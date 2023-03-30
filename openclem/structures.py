from dataclasses import dataclass
from enum import Enum


class TriggerEdge(Enum):
    """Trigger edge"""

    RISING = 1
    FALLING = 2

class TriggerSource(Enum):
    """Trigger source"""

    SOFTWARE = 1
    EXTERNAL = 2
    INTERNAL = 3

class ExposureMode(Enum):
    """Exposure mode"""

    TIMED = 1
    TRIGGER_WIDTH = 2


@dataclass
class ImageSettings:
    """Image settings"""

    pixel_size: float = 0.0
    exposure: float = 0.0
    image_format: str = "tiff"
    n_images: int = 1

    @staticmethod
    def __from_dict__(settings: dict) -> "ImageSettings":
        return ImageSettings(
            pixel_size=settings["pixel_size"],
            exposure=settings["exposure"],
            image_format=settings["image_format"],
            n_images=settings["n_images"],
        )

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "pixel_size": self.pixel_size,
            "exposure": self.exposure,
            "image_format": self.image_format,
            "n_images": self.n_images,
        }


@dataclass
class SerialSettings:
    """Serial settings"""

    port: str = None
    baudrate: int = 9600
    timeout: float = 0.1

    @staticmethod
    def __from_dict__(settings: dict) -> "SerialSettings":
        # TODO: check if this is ok
        if settings is None:
            return None
        return SerialSettings(
            port=settings["port"],
            baudrate=settings["baudrate"],
            timeout=settings["timeout"],
        )

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "port": self.port,
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
class LaserControllerSettings:
    """Laser controller settings"""

    name: str
    serial_settings: SerialSettings
    laser: str

    @staticmethod
    def __from_dict__(settings: dict) -> "LaserControllerSettings":

        laser_controller_settings = LaserControllerSettings(
            name=settings["name"],
            serial_settings=SerialSettings.__from_dict__(settings["serial"]),
            laser=settings["laser"],
        )
        return laser_controller_settings

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "serial_settings": SerialSettings.__to_dict__(self.serial_settings),
            "laser": self.laser,
        }

@dataclass
class DetectorSettings:
    """Detector settings"""

    name: str
    serial_settings: SerialSettings
    pixel_size: float
    resolution: list[int]
    trigger_source: TriggerSource = TriggerSource.SOFTWARE
    trigger_edge: TriggerEdge = TriggerEdge.RISING
    exposure_mode: ExposureMode = ExposureMode.TRIGGER_WIDTH
    timeout: int = 1000 # ms

    @staticmethod
    def __from_dict__(settings: dict) -> "DetectorSettings":

        detector_settings = DetectorSettings(
            name=settings["name"],
            serial_settings=SerialSettings.__from_dict__(settings["serial"]),
            pixel_size=settings["pixel_size"],
            resolution=settings["resolution"],
            trigger_source=TriggerSource[settings["trigger_source"]],
            trigger_edge=TriggerEdge[settings["trigger_edge"]],
            exposure_mode=ExposureMode[settings["exposure_mode"]],
            timeout=settings["timeout"],
        )
        return detector_settings

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "serial_settings": SerialSettings.__to_dict__(self.serial_settings),
            "pixel_size": self.pixel_size,
            "resolution": self.resolution,
            "trigger_source": self.trigger_source.name,
            "trigger_edge": self.trigger_edge.name,
            "exposure_mode": self.exposure_mode.name,
            "timeout": self.timeout,
        }

@dataclass
class SynchroniserSettings:
    name: str
    pins: dict[str: int]
    serial_settings: SerialSettings = None

    @staticmethod
    def __from_dict__(settings: dict) -> "SynchroniserSettings":

            trigger_settings = SynchroniserSettings(
                name=settings["name"],
                pins=settings["pins"],
                serial_settings=SerialSettings.__from_dict__(settings["serial"]),
            )
            return trigger_settings

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "pins": self.pins,
            "serial_settings": None if self.serial_settings is None else SerialSettings.__to_dict__(self.serial_settings),
        }

@dataclass
class SynchroniserMessage:
    """Synchroniser message"""

    exposures: list[float]
    pins: dict[str: int]
    mode: str = "single"
    n_slices: int = 0
    trigger_edge: TriggerEdge = TriggerEdge.RISING

    @staticmethod
    def __from_dict__(settings: dict) -> "SynchroniserMessage":
        synchroniser_message = SynchroniserMessage(
            exposures=settings["exposures"],
            pins=settings["pins"],
            mode=settings["mode"],
            n_slices=settings["n_slices"],
            trigger_edge=TriggerEdge[settings["trigger_edge"]],
        )
        return synchroniser_message

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "exposures": self.exposures,
            "pins": self.pins,
            "mode": self.mode,
            "n_slices": self.n_slices,
            "trigger_edge": self.trigger_edge.name,
        }

@dataclass
class MicroscopeSettings:
    """Microscope settings"""

    name: str
    lasers: list[LaserSettings]
    detector: DetectorSettings = None
    laser_controller: LaserControllerSettings = None

    @staticmethod
    def __from_dict__(settings: dict) -> "MicroscopeSettings":

        microscope_settings = MicroscopeSettings(
            name=settings["name"],
            detector=DetectorSettings.__from_dict__(settings["detector"]),
            laser_controller=LaserControllerSettings.__from_dict__(settings["laser_controller"]),
            lasers=[LaserSettings.__from_dict__(laser) for laser in settings["lasers"]],
        )
        return microscope_settings

    @staticmethod
    def __to_dict__(self) -> dict:
        return {
            "name": self.name,
            "detector": DetectorSettings.__to_dict__(self.detector),
            "laser_controller": LaserControllerSettings.__to_dict__(self.laser_controller),
            "lasers": [LaserSettings.__to_dict__(laser) for laser in self.lasers],
        }
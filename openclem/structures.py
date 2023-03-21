from enum import Enum
from dataclasses import dataclass

class TriggerMode(Enum):
    """Trigger mode"""
    INTERNAL = 1
    EXTERNAL = 2
    SOFTWARE = 3

class TriggerEdge(Enum):
    """Trigger edge"""
    RISING = 1
    FALLING = 2

class ExposureMode(Enum):
    """Exposure mode"""
    EXPOSURE = 1
    TRIGGERWIDTH = 2

@dataclass
class ImageSettings:
    """Image settings"""
    exposure: float = 0.0
    trigger_mode: TriggerMode = TriggerMode.SOFTWARE
    trigger_edge: TriggerEdge = TriggerEdge.RISING
    exposure_mode: ExposureMode = ExposureMode.EXPOSURE
    trigger_width: float = 0.0
    binning: int = 1
    gain: int = 1
    offset: int = 0
    roi: tuple = (0, 0, 0, 0)
    image_format: str = 'tiff'

@dataclass
class LaserSettings:
    """Laser settings"""
    wavelength: float = 0.0
    power: float = 0.0

@dataclass
class AvailableLasers:
    """Laser group"""
    lasers: list = None


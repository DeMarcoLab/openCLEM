from abc import ABC, abstractmethod
from openclem.structures import ImageSettings
import numpy as np


class Detector(ABC):

    # assumption is that the detector is connected to the computer via a serial port
    @abstractmethod
    def connect(self, port: str, baudrate: int, timeout: float) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def init_camera(self):
        pass

    @abstractmethod
    def open_camera(self):
        pass

    @abstractmethod
    def close_camera(self):
        pass

    @property
    @abstractmethod
    def exposure_mode(self):
        pass

    @property
    @abstractmethod
    def exposure_time(self):
        pass

    @property
    @abstractmethod
    def pixel_size(self):
        pass

    @abstractmethod
    def grab_image(self, image_settings: ImageSettings = None) -> np.ndarray:
        pass
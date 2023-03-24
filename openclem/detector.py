from abc import ABC, abstractmethod
from openclem.structures import ImageSettings, DetectorSettings
import numpy as np


class Detector(ABC):

    def __init__(self, detector_settings: DetectorSettings):
        self.settings = detector_settings
        self.camera = None
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
        """Trigger or level"""
        pass

    @property
    @abstractmethod
    def trigger_edge(self):
        """Rising or Falling"""
        pass

    @property
    @abstractmethod
    def trigger_source(self):
        """Internal, External, Software"""
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
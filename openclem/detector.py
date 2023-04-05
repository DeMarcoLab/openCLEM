from abc import ABC, abstractmethod
from openclem.structures import (ImageSettings, DetectorSettings, 
    ExposureMode, TriggerEdge, TriggerSource)
import numpy as np

from queue import Queue
import threading

class Detector(ABC):

    def __init__(self, detector_settings: DetectorSettings):
        self.camera = None
        self.connection = None
        self.set(detector_settings)

    def set(self, detector_settings: DetectorSettings):

        # TODO: _START_HERE - add code to update the detector settings
        self.name = detector_settings.name
        self.connection = detector_settings.connection
        self.pixel_size = detector_settings.pixel_size
        self.resolution = detector_settings.resolution
        self.exposure_mode = detector_settings.exposure_mode
        self.trigger_edge = detector_settings.trigger_edge
        self.trigger_source = detector_settings.trigger_source

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

    @exposure_mode.setter
    def exposure_mode(self, value: ExposureMode):
        pass

    @property
    @abstractmethod
    def trigger_edge(self) -> TriggerEdge:
        """Rising or Falling"""
        pass

    @trigger_edge.setter
    def trigger_edge(self, value: TriggerEdge):
        pass

    @property
    @abstractmethod
    def trigger_source(self) -> TriggerSource:
        """Internal, External, Software"""
        pass

    @trigger_source.setter
    def trigger_source(self, value: TriggerSource):
        pass

    @property
    @abstractmethod
    def exposure_time(self) -> float:
        pass

    @exposure_time.setter
    def exposure_time(self, value: float):  
        pass

    @property
    @abstractmethod
    def pixel_size(self) -> float:
        pass

    @pixel_size.setter
    def pixel_size(self, value: float):
        pass

    @property
    def resolution(self) -> tuple[int]:
        return self._resolution

    @resolution.setter
    def resolution(self, value: tuple[int]):
        self._resolution = value

    @abstractmethod
    def grab_image(self, image_settings: ImageSettings, image_queue: Queue, stop_event: threading.Event) -> np.ndarray:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.settings})"
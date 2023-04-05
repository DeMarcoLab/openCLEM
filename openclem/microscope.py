from abc import ABC, abstractmethod
from openclem.structures import ImageSettings, LaserSettings
from openclem.laser import LaserController, Laser
from openclem.objective import ObjectiveStage
from openclem.detector import Detector
from openclem.synchronisation import Synchroniser

import logging
import threading
from queue import Queue

class LightMicroscope(ABC):
    """Abstract class for light microscope"""
    def __init__(self, name: str):
        self.name = name
        self._connection = None
        self._detector: Detector = None
        self._objective: ObjectiveStage = None
        self._laser_controller: LaserController = None

    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def add_detector(self, detector: Detector):
        pass
    
    @abstractmethod
    def get_detector(self) -> Detector:
        return self.detector
    
    @abstractmethod
    def add_objective(self, objective: ObjectiveStage):
        pass

    @abstractmethod
    def get_objective(self) -> ObjectiveStage:
        return self.objective
    
    @abstractmethod
    def add_laser_controller(self, laser_controller: LaserController):
        pass

    @abstractmethod
    def get_laser_controller(self) -> LaserController:
        return self.laser_controller
    
    @abstractmethod
    def add_synchroniser(self, synchroniser: Synchroniser):
        pass

    @abstractmethod
    def get_synchroniser(self) -> Synchroniser:
        pass

    @abstractmethod
    def setup_acquisition(self):
        pass

    @abstractmethod
    def acquire_image(self, image_settings:ImageSettings) -> tuple[Queue, threading.Event]:
        pass

    @abstractmethod
    def live_image(self, image_settings:ImageSettings):
        pass
    
    @abstractmethod
    def consume_image(self, image_queue:Queue, stop_event: threading.Event):
        pass

    def get_lasers(microscope) -> list[LaserSettings]:
        lasers = microscope.get_laser_controller().lasers
        return [microscope.get_laser_controller().get_laser(laser) for laser in lasers]

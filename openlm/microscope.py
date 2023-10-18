from abc import ABC, abstractmethod
from openlm.structures import ImageSettings, LaserSettings
from openlm.laser import LaserController, Laser
from openlm.objective import ObjectiveStage
from openlm.detector import Detector
from openlm.synchronisation import Synchroniser

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
        self._synchroniser: Synchroniser = None

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
    def consume_image_queue(self):
        pass

    def get_lasers(microscope) -> list[LaserSettings]:
        lasers = microscope.get_laser_controller().lasers
        return [microscope.get_laser_controller().get_laser(laser).get() for laser in lasers]

    @abstractmethod
    def move_stage(dx:float, dy:float, dz:float):
        pass

    @abstractmethod
    def move_objective_stage(dz:float):
        pass
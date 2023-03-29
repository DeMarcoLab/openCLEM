from openclem.microscope import LightMicroscope

from openclem.structures import ImageSettings
from openclem.laser import LaserController
from openclem.objective import Objective
from openclem.detector import Detector


class PIEDISCMicroscope(LightMicroscope):

    def __init__(self, name: str):
        super().__init__(name)
        self._connection = None
        self._detector = None
        self._objective = None
        self._laser_controller = None


    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialise(self):
        pass

    def add_detector(self, detector: Detector):
        self._detector = detector

    def get_detector(self) -> Detector:
        return self._detector
    
    def add_objective(self, objective: Objective):
        self._objective = objective

    def get_objective(self) -> Objective:
        return self._objective
    
    def add_laser_controller(self, laser_controller: LaserController):

        self._laser_controller = laser_controller

    def get_laser_controller(self) -> LaserController:
        return self._laser_controller
    
    def acquire_image(self, image_settings:ImageSettings):
        pass

    def live_image(self, image_settings:ImageSettings):
        pass

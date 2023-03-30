from openclem.microscope import LightMicroscope

from openclem.structures import ImageSettings
from openclem.laser import LaserController
from openclem.objective import ObjectiveStage
from openclem.detector import Detector
from openclem.synchronisation import Synchroniser

class BaseLightMicroscope(LightMicroscope):

    def __init__(self, name: str):
        self.name = name
        self._connection = None
        self._detector = None
        self._objective = None
        self._laser_controller = None

    def connect(self):
        self._detector.connect()
        self._laser_controller.connect()
        self._objective.connect()
        self._synchroniser.connect()

    def disconnect(self):
        self._detector.disconnect()
        self._laser_controller.disconnect()
        self._objective.disconnect()
        
    def initialise(self):
        # self._detector.initialise() # REFACTOR
        # self._laser_controller.initialise() # REFACTOR
        self._objective.initialise()

    def add_detector(self, detector: Detector):
        self._detector = detector

    def get_detector(self) -> Detector:
        return self._detector
    
    def add_objective(self, objective: ObjectiveStage):
        self._objective = objective

    def get_objective(self) -> ObjectiveStage:
        return self._objective
    
    def add_laser_controller(self, laser_controller: LaserController):
        self._laser_controller = laser_controller

    def get_laser_controller(self) -> LaserController:
        return self._laser_controller
    
    def add_synchroniser(self, synchroniser) -> None:
        self._synchroniser = synchroniser

    def get_synchroniser(self) -> Synchroniser:
        return self._synchroniser

    def acquire_image(self, image_settings:ImageSettings):
        
        image = self._detector.grab_image(image_settings)

        return image

    def live_image(self, image_settings:ImageSettings):
        pass

# system.yaml -> LightMicroscope
# microscope.acquire_image(microscope, image_settings)
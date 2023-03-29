from abc import ABC, abstractmethod
from openclem.structures import ImageSettings
from openclem.detector import Detector
from openclem.laser import LaserController, Laser

class LightMicroscope(ABC):
    """Abstract class for light microscope"""
    def __init__(self, detector: Detector, laser_controller: LaserController, laser: Laser):
        self.detector = detector
        self.laser_controller = laser_controller
        self.laser = laser

    @abstractmethod
    def connect_to_microscope(self):
        self.detector.connect()
        self.laser_controller.connect()
    
    @abstractmethod
    def disconnect(self):
        self.detector.disconnect()
        self.laser_controller.disconnect()

    # @abstractmethod
    # def acquire_image(self, image_settings:ImageSettings):
    #     pass

    # @abstractmethod
    # def live_image(self, image_settings:ImageSettings):
    #     pass

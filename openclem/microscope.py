from abc import ABC, abstractmethod
from openclem.structures import ImageSettings

class LightMicroscope(ABC):
    """Abstract class for light microscope"""

    @abstractmethod
    def connect_to_microscope(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass

    # @abstractmethod
    # def acquire_image(self, image_settings:ImageSettings):
    #     pass

    # @abstractmethod
    # def live_image(self, image_settings:ImageSettings):
    #     pass

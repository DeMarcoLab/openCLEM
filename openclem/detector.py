from abc import ABC, abstractmethod

class Detector(ABC):
    @property
    @abstractmethod
    def name(self):
        pass
    
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def grab_single_image(self):
        pass

    @abstractmethod
    def grab_continuous_images(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def set_image_settings(self, image_settings):
        pass

    @abstractmethod
    def get_image_settings(self):
        pass

    @abstractmethod
    def init_camera(self):
        pass

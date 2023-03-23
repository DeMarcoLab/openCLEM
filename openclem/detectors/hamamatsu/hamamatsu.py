from openclem.detector import Detector
from openclem.detectors.hamamatsu.dcam import *

class Hamamatsu(Detector):
    def __init__(self):
        self.name = 'Hamamatsu Detector'
        
    def init_camera(self):
        if Dcamapi.init() != DCAMERR_NONE:
            raise Exception('Failed to initialize the camera')

    def connect(self):
        pass

    def disconnect(self):
        pass

    def grab_single_image(self):
        pass

    def grab_continuous_images(self):
        pass

    def close(self):
        pass

    def open(self):
        pass

    def set_image_settings(self, image_settings):
        pass

    def get_image_settings(self):
        pass

    def init_camera(self):
        pass
from openclem.detector import Detector
from pypylon import pylon

class Basler(Detector):
    def __init__(self):
        self.name = 'Basler Detector'
        
    def init_camera(self):
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )

    def connect(self):
        pass

    def disconnect(self):
        pass

    
import logging
from openclem.detector import Detector
from openclem.structures import ImageSettings, DetectorSettings, ExposureMode, ImageMode, TriggerEdge, TriggerSource
import numpy as np
import time

from queue import Queue
import threading

class DemoDetector(Detector):

    def __init__(self, detector_settings: DetectorSettings):
        self.settings = detector_settings
        self.camera = None
        self.serial_connection = None
        self.name = detector_settings.name

        # ? why not just use the settings?
        self._trigger_source = None
        self._trigger_edge = None
        self._exposure_mode = None
        self._exposure_time = None
        self._pixel_size = None


    @classmethod
    def __id__(self):
        return "demo"
    
    def connect(self) -> None:
        logging.info(f"Connecting to Demo Detector...")
        time.sleep(1)
        logging.info(f"Connected to Demo Detector.")
    
    def disconnect(self) -> None:
        logging.info("Disconnecting from Demo Detector")
        time.sleep(1)
        logging.info("Disconnected from Demo Detector")

    
    def init_camera(self):
        logging.info("Initializing Demo Camera")
        self.camera = "DemoCamera"
        logging.info(f"Initialized Demo Camera: {self.camera}")

    
    def open_camera(self):
        logging.info("Opening Demo Camera")

    
    def close_camera(self):
        logging.info("Closing Demo Camera")

    @property
    def exposure_mode(self):
        """Trigger or level"""
        return self._exposure_mode
    
    @exposure_mode.setter
    def exposure_mode(self, value: ExposureMode):
        self._exposure_mode = value

    @property
    def trigger_edge(self):
        """Rising or Falling"""
        return self._trigger_edge
    
    @trigger_edge.setter
    def trigger_edge(self, value: TriggerEdge):
        self._trigger_edge = value

    @property
    def trigger_source(self):
        """Internal, External, Software"""
        return self._trigger_source
    
    @trigger_source.setter
    def trigger_source(self, value: TriggerSource):
        self._trigger_source = value

    @property
    def exposure_time(self):
        return self._exposure_time
    
    @exposure_time.setter
    def exposure_time(self, value: float):
        self._exposure_time = value

    @property
    def pixel_size(self):
        return self._pixel_size
    
    @pixel_size.setter
    def pixel_size(self, value: float):
        self._pixel_size = value
    
    def grab_image(self, image_settings: ImageSettings, image_queue: Queue, stop_event: threading.Event) -> np.ndarray:
        if self.camera is None or image_settings is None: return
        logging.info("Grabbing image from Demo Camera")
        image = None
        
        try:
            # open camera
            self.open_camera()

            logging.info(f"Image Settings: {image_settings}")
            count = image_settings.n_images
            count_ = 0
            while count_ < count and not stop_event.is_set():
                
                # acquire image
                time.sleep(image_settings.exposure)
                image = np.random.randint(0, 255, size=self.settings.resolution, dtype=np.uint8)
                
                if image_queue:
                    image_queue.put(image)
                    # logging.info(f"Putting image {count_} in queue: {image.shape}, {np.mean(image):.2f}")
                
                if image_settings.mode == ImageMode.SINGLE:
                    count_ += 1

                # logging.info(f"COUNT: {count_}, STOP_EVENT: {stop_event.is_set()}")
            
        except Exception as e:
            logging.error(f"Could not grab image from Demo Camera: {e}")
        finally:
            self.close_camera()
            time.sleep(0.5)
            stop_event.set()
        
        return
        # return image

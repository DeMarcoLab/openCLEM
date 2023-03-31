from openclem.microscope import LightMicroscope

from openclem.structures import ImageSettings, SynchroniserMessage
from openclem.laser import LaserController
from openclem.objective import ObjectiveStage
from openclem.detector import Detector
from openclem.synchronisation import Synchroniser

import logging
import time
import threading
from queue import Queue 
import numpy as np

class BaseLightMicroscope(LightMicroscope):

    def __init__(self, name: str):
        self.name = name
        self._connection = None
        self._detector = None
        self._objective = None
        self._laser_controller = None
        self._synchroniser = None

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

    def setup_acquisition(self):
        # laser settings, detector settings
        #  
        # Set up lasers
        for laser in self._laser_controller.lasers:
            self._laser_controller.set_power(laser, 4.0)
        # TODO: add in laser_settings for hardware triggering

    def acquire_image(self, image_settings:ImageSettings, sync_message: SynchroniserMessage):

        # Set up detector
        self._detector.init_camera()

        stop_event = threading.Event()
        image_queue = Queue()
        _thread = threading.Thread(
            target=_threaded_grab_image, 
            args=(self, image_settings, image_queue, stop_event)
        )
        _thread.start()
        time.sleep(1) # wait for the camera to get ready

        # Run sync
        self.get_synchroniser().sync_image(sync_message)

        # poll until keyboard interrupt
        try:
            i = 0
            while True:
                logging.info(f"Thread alive: {_thread.is_alive()}")
                image = image_queue.get()
                logging.info(f"Getting image {i} in queue: {image.shape}, {np.mean(image)}")

                np.save(f"image_{i:02d}.npy", image)
                time.sleep(0.1)
                i+=1

        except KeyboardInterrupt:
            stop_event.set()
            logging.info("Keyboard interrupt")
        finally:
            logging.info("Thread stopped.")

    def live_image(self, image_settings:ImageSettings):
        return


def _threaded_grab_image(microscope: LightMicroscope, 
                                image_settings:ImageSettings, image_queue: Queue, 
                                stop_event: threading.Event
                                ):
        
        microscope._detector.grab_image(image_settings, image_queue)

# system.yaml -> LightMicroscope
# microscope.acquire_image(microscope, image_settings)
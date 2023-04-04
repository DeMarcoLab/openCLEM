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
        self._synchroniser.disconnect()

    def initialise(self):
        # self._detector.initialise() # REFACTOR
        # self._laser_controller.initialise() # REFACTOR
        # self._objective.initialise()
        self._laser_controller.initialise() # mvoe to INIT

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

        for laser in self._laser_controller.lasers:
            logging.info(f"Laser: {laser}: {self._laser_controller.get_power(laser)}")

    def acquire_image(
        self, image_settings: ImageSettings, 
        sync_message: SynchroniserMessage, 
        stop_event: threading.Event= threading.Event()
    ):
        # Set up detector # TODO: move this into initialise
        self._detector.init_camera()

        # start thread
        image_queue = Queue()
        _thread = threading.Thread(
            target=self._detector.grab_image,
            args=(image_settings, image_queue, stop_event),
        )
        _thread.start()
        time.sleep(1)  # wait for the camera to get ready

        # Run sync
        self.get_synchroniser().sync_image(sync_message)

        self.image_queue = image_queue
        self.stop_event = stop_event
        self.sync_message = sync_message
        self.image_settings = image_settings
        return self.image_queue, self.stop_event

    def live_image(self, image_settings: ImageSettings):
        return

    def consume_image(self, viz: bool = False):
                
        if self.image_queue is None:
            raise ValueError("No image queue found. Run acquire_image first.")

        if self.stop_event is None:
            raise ValueError("No stop event found. Run acquire_image first.")

        # poll until keyboard interrupt
        try:
            counter = 0
            while self.image_queue.qsize() > 0 and not self.stop_event.is_set():
                image = self.image_queue.get()
                
                logging.info(f"Getting img {counter%4} in queue: {image.shape}, {np.mean(image)}"
                )

                # save image with PIL
                # print(type(image))
                # image = Image.fromarray(image)
                # print(image)
                # image.save(f"image_{i:03d}.png") 
                # time.sleep(0.1)

                if viz:
                    yield (image, f"Channel {counter % 4:02d}")
                counter += 1

        except KeyboardInterrupt:
            self.stop_event.set()
            logging.info("Keyboard interrupt")
        finally:
            self.get_synchroniser().stop_sync()
            logging.info("Thread stopped.")


from queue import Queue
import threading
from openclem.microscope import LightMicroscope

from openclem import utils
from openclem.structures import LightImage, LightImageMetadata

def consume_image_queue(microscope:LightMicroscope, image_queue:Queue, stop_event: threading.Event,  viz=False):

    # get index of non-zero exposures
    exposure_indices = [i for i, v in enumerate(microscope.sync_message.exposures) if v > 0]
    n_exposures = len(exposure_indices)

    logging.info(f"Exposure indices: {exposure_indices}")
    logging.info(f"Number of exposures: {n_exposures}")

    metadata = LightImageMetadata(
        n_channels=n_exposures,
        channels=exposure_indices,
        lasers=microscope.get_lasers(),
        time=utils.current_timestamp(),
        detector=microscope.get_detector().settings,
        objective=microscope.get_objective().position,
        image= microscope.image_settings,
        sync=microscope.sync_message,
    )

    try:
        counter = 0
        while image_queue.qsize() > 0 or not stop_event.is_set():
            
            channel = counter % n_exposures # TODO: probably should pass this info out of the queue? but how

            image = image_queue.get()
            if channel == 0:
                arr = image
                # expand dims to add channel axis
                arr = np.expand_dims(arr, axis=-1)
            else:
                arr = np.dstack((arr, image))

            if channel == n_exposures - 1:
                image = LightImage(
                    data=arr,
                    metadata=metadata,
                )
                image.metadata.time = utils.current_timestamp()
            
                logging.info(f"Image: {image.data.shape} {image.metadata.time}")
                logging.info(f"-"*50)

            if viz:
                print(image, f"Channel {channel:02d}")
            counter += 1

    except KeyboardInterrupt:
        stop_event.set()
        logging.info("Keyboard interrupt")
    except Exception as e:
        stop_event.set()
        logging.error(e)
    finally:
        microscope.get_synchroniser().stop_sync()
        logging.info("Thread stopped.")

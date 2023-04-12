import logging
import threading
import time
import traceback
from queue import Queue

import numpy as np

from openclem import utils
from openclem.detector import Detector
from openclem.laser import LaserController
from openclem.microscope import LightMicroscope
from openclem.objective import ObjectiveStage
from openclem.structures import (ImageSettings, LightImage, LightImageMetadata,
                                 SynchroniserMessage)
from openclem.synchronisation import Synchroniser


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

        # for laser in self._laser_controller.lasers:
            # self._laser_controller.set_power(laser, 4.0)
            # self._laser_controller.set_power(laser, laser_settings.power)
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

    def _update_image_metadata(self) -> LightImageMetadata:
        # update image metadata

        # get index of non-zero exposures
        exposure_indices = [i for i, v in enumerate(self.sync_message.exposures) if v > 0]
        n_channels = len(exposure_indices)

        logging.info(f"Exposure indices: {exposure_indices}")
        logging.info(f"Number of exposures: {n_channels}")

        metadata = LightImageMetadata(
            n_channels=n_channels,
            channels=exposure_indices,
            lasers=self.get_lasers(),
            time=utils.current_timestamp(),
            detector=self.get_detector().settings,
            objective=self.get_objective().position,
            image= self.image_settings,
            sync=self.sync_message,
        )
        return metadata
    
    # TODO: consolidate these two functions when you are smarter

    def consume_image_queue(self):

        # update metadata
        metadata = self._update_image_metadata()

        # consume queue
        try:
            counter = 0
            while self.image_queue.qsize() > 0 or not self.stop_event.is_set():
                
                # get image
                image = self.image_queue.get()
                
                channel = counter % metadata.n_channels 
                if channel == 0:
                    # expand dims to add channel axis
                    arr = np.expand_dims(image, axis=-1)
                else:
                    arr = np.dstack((arr, image))

                if channel == metadata.n_channels - 1:
                    image = LightImage(
                        data=arr,
                        metadata=metadata,
                    )
                    image.metadata.time = utils.current_timestamp()
                    
                    import os
                    fname = os.path.join(os.getcwd(), str(image.metadata.time))
                    image.save(fname)
                    logging.info(f"Image: {image.data.shape} {image.metadata.time}")
                    logging.info(f"-"*50)

                counter += 1

        except KeyboardInterrupt:
            self.stop_event.set()
            logging.info("Keyboard interrupt")
        except Exception as e:
            self.stop_event.set()
            logging.error(traceback.format_exc())
        finally:
            self.get_synchroniser().stop_sync()
            logging.info("Thread stopped.")
    
    from napari.qt.threading import thread_worker
    @thread_worker
    def consume_image_queue_ui(self):

        # update metadata
        metadata = self._update_image_metadata()

        # consume queue
        try:
            counter = 0
            while self.image_queue.qsize() > 0 or not self.stop_event.is_set():
                
                # get image
                image = self.image_queue.get()

                channel = counter % metadata.n_channels 
                if channel == 0:
                    # expand dims to add channel axis
                    arr = np.expand_dims(image, axis=-1)
                else:
                    arr = np.dstack((arr, image))

                if channel == metadata.n_channels - 1:
                    image = LightImage(
                        data=arr,
                        metadata=metadata,
                    )
                    image.metadata.time = utils.current_timestamp()
                    
                    save = False
                    if save:
                        import os
                        fname = os.path.join(os.getcwd(), str(image.metadata.time))
                        image.save(fname)
                    logging.info(f"Image: {image.data.shape} {image.metadata.time}")
                    logging.info(f"-"*50)

                    yield image
                counter += 1

        except Exception as e:
            self.stop_event.set()
            logging.error(traceback.format_exc())
        finally:
            self.get_synchroniser().stop_sync()
            logging.info("Thread stopped.")
        
        return
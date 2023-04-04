import os
from openclem import utils
from openclem import config
from openclem.structures import ImageMode, SynchroniserMessage, ImageSettings, DetectorSettings
import time
import logging
import numpy as np
from PIL import Image


from dataclasses import dataclass
from openclem.structures import (LaserSettings, ImageMode, TriggerEdge, TriggerSource, 
    DetectorSettings, ObjectiveSettings)


cfg_path = os.path.join(config.BASE_PATH, "config", "system.yaml")
# cfg_path = os.path.join(config.BASE_PATH, "config", "piedisc.yaml")
cfg = utils.load_yaml(cfg_path)
microscope, settings = utils.setup_session(config_path=cfg_path)

# microscope._objective.relative_move(1e-3)
# print(microscope._objective.position)

microscope._laser_controller.initialise() # TODO: move to init @DavidDierickx

# time.sleep(3)
# microscope.get_synchroniser().stop_sync()
microscope.setup_acquisition()
mode = ImageMode.LIVE

# Set up sync
# sync_message = SynchroniserMessage.__from_dict__({
#     "exposures": [1000, 0, 1000, 1000],
#     "pins": {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
#     "mode": mode.value,
#     "n_slices": 4,
#     "trigger_edge": "RISING",
# })

sync_message = SynchroniserMessage(
    exposures= [1000, 0, 1000, 1000],
    pins=  {"laser1": 1, "laser2": 2, "laser3": 3, "laser4": 4},
    mode=mode,
    n_slices = 4,
    trigger_edge = TriggerEdge.RISING,
)


image_settings = ImageSettings(
    pixel_size=25e-6,
    exposure=500.e-3,
    n_images = 4,
    mode=mode,
)

image_queue, stop_event = microscope.acquire_image(
    image_settings=image_settings, 
    sync_message=sync_message)

time.sleep(1) # wait for camera to start?




@dataclass
class LightImageMetadata:
    n_channels: int                 # number of channels
    channels: list[int]             # channel indices
    time: float                     # time of acquisition
    lasers: list[LaserSettings]     # laser settings
    detector: DetectorSettings      # detector settings
    objective: ObjectiveSettings    # objective settings
    image: ImageSettings            # image settings
    sync: SynchroniserMessage       # sync settings

    def __to_dict__(self) -> dict:
        return dict(
            n_channels=self.n_channels,
            channels=self.channels,
            time=self.time,
            lasers=[l.__to_dict__() for l in self.lasers],
            detector=self.detector.__to_dict__(),
            objective=self.objective.__to_dict__(),
            image=self.image.__to_dict__(),
            sync=self.sync.__to_dict__(),
        )
    
    
    @classmethod
    def __from_dict__(cls, data: dict) -> "LightImageMetadata":
        return cls(
            n_channels=data["n_channels"],
            channels=data["channels"],
            time=data["time"],
            lasers=[LaserSettings.__from_dict__(l) for l in data["lasers"]],
            detector=DetectorSettings.__from_dict__(data["detector"]),
            objective=ObjectiveSettings.__from_dict__(data["objective"]),
            image=ImageSettings.__from_dict__(data["image"]),
            sync=SynchroniserMessage.__from_dict__(data["sync"]),
        )
    
    def __repr__(self) -> str:
        return f"LightImageMetadata(n_channels={self.n_channels}, channels={self.channels}, time={self.time}, lasers={self.lasers}, detector={self.detector}, objective={self.objective}, image={self.image}, sync={self.sync})"

@dataclass
class LightImage:
    data: np.ndarray
    metadata: LightImageMetadata

    def __to_dict__(self) -> dict:
        return dict(
            data=self.data,
            metadata=self.metadata.__to_dict__(),
        )
    
    @classmethod
    def __from_dict__(cls, data: dict) -> "LightImage":
        return cls(
            data=data["data"],
            metadata=LightImageMetadata.__from_dict__(data["metadata"]),
        )

    def __repr__(self) -> str:
        
        return "\n".join([
            f"image: {self.data.shape}"
            f"metadata: {self.metadata}"])



# metadata
#       channel
#       time
#       laser

#    position
#    slice
#    z
#    t
#    exposure
#    pixel_size
#    mode
#    n_images
#    n_slices

# what were the settings?
# for the laser
# for the detector
# for the stage
# for the objective
# for the synchroniser
# what was the image


from queue import Queue
import threading



# detector_settings
# laser_settings for each laser
# objective_settings
# stage_settings
# synchroniser_settings
# image_settings


# tmp
def get_lasers(microscope) -> list[LaserSettings]:
    lasers = microscope.get_laser_controller().lasers
    return [microscope.get_laser_controller().get_laser(laser) for laser in lasers]


def consume_image_queue(image_queue:Queue, stop_event: threading.Event, sync_message: SynchroniserMessage, viz=False):

    # get index of non-zero exposures
    exposure_indices = [i for i, v in enumerate(sync_message.exposures) if v > 0]
    n_exposures = len(exposure_indices)

    logging.info(f"Exposure indices: {exposure_indices}")
    logging.info(f"Number of exposures: {n_exposures}")

    metadata = LightImageMetadata(
        n_channels=n_exposures,
        channels=exposure_indices,
        lasers=get_lasers(microscope),
        time=utils.current_timestamp(),
        detector=microscope.get_detector().settings,
        objective=microscope.get_objective().position,
        image= image_settings,
        sync=sync_message,
    )

    try:
        counter = 0
        while image_queue.qsize() > 0 or not stop_event.is_set():
            
            # stack the image channels into a single image
            # arr = np.stack([image_queue.get().data for _ in range(n_exposures)], axis=-1)

            channel = counter % n_exposures

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
            
                logging.info(f"Image: {image}")
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

consume_image_queue(image_queue, stop_event, sync_message, viz=False)


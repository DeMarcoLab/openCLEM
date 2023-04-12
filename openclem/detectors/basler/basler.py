import logging

from pypylon import pylon

from openclem import utils
from openclem.detector import Detector
from openclem.structures import ImageSettings, DetectorSettings, ExposureMode
import numpy as np


class BasleracA1920_155um(Detector):
    def __init__(self, detector_settings: DetectorSettings):
        self.settings = detector_settings
        self.name = "Basler Detector"
        self.connection = None
        self.camera = None
        self._pixel_size = 5.86e-6

    @classmethod
    def __id__(self):
        return "basler"

    def connect(self) -> None:
        serial_settings = self.settings.serial_settings
        logging.info("Connecting to Basler detector on port: %s", serial_settings.port)
        self.connection = utils.connect_to_serial_port(
            serial_settings=serial_settings
        )
        logging.info("Connected to Basler detector on port: %s", serial_settings.port)


    def disconnect(self):
        if self.connection is None:
            logging.info("No Basler detector to disconnect from")
            return

        logging.info("Disconnecting from Basler detector")
        self.connection.close()
        logging.info("Disconnected from Basler detector")

    def init_camera(self):
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )

    def open_camera(self):
        if self.camera is not None:
            self.camera.Open()

    def close_camera(self):
        if self.camera is not None:
            self.camera.Close()

    def grab_image(self, image_settings: ImageSettings = None) -> np.ndarray:
        if self.camera is None or image_settings is None: return
        self.open_camera()
        self.camera.StopGrabbing()

        self.exposure_time = image_settings.exposure

        self.camera.StartGrabbingMax(1)
        image = None
        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException
            )
            if grabResult.GrabSucceeded():
                image = grabResult.Array
                return image

    @property
    def exposure_time(self):
        try:
            return self.camera.ExposureTime.GetValue()
        except Exception as e:
            return self.camera.ExposureTimeAbs.GetValue()

    @exposure_time.setter
    def exposure_time(self, exposure_time: float = None):
        if exposure_time is None:
            return
        try:
            self.camera.ExposureTime.SetValue(exposure_time)
        except Exception as e:
            self.camera.ExposureTimeAbs.SetValue(exposure_time)

    @property
    def exposure_mode(self):
        return self.camera.ExposureMode.GetValue()

    @exposure_mode.setter
    def exposure_mode(self, exposure_mode: ExposureMode = None):
        if exposure_mode is None:
            return
        if exposure_mode == ExposureMode.TIMED:
            self.camera.ExposureMode.SetValue("Timed")
        elif exposure_mode == ExposureMode.TRIGGER_WIDTH:
            self.camera.ExposureMode.SetValue("TriggerWidth")
            self.camera.AcquisitionFrameRateEnable.SetValue(False)

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, pixel_size: float = None):
        if pixel_size is None:
            return
        self._pixel_size = pixel_size

    @property
    def trigger_edge(self):
        return self.camera.TriggerSelector.GetValue()

    @trigger_edge.setter
    def trigger_edge(self, trigger_edge: str = None):
        if trigger_edge is None:
            return
        self.camera.TriggerSelector.SetValue(trigger_edge)

    @property
    def trigger_source(self):
        return self.camera.TriggerSource.GetValue()

    @trigger_source.setter
    def trigger_source(self, trigger_source: str = None):
        if trigger_source is None:
            return
        self.camera.TriggerSource.SetValue(trigger_source)

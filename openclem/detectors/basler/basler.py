import logging

from pypylon import pylon

from openclem import utils
from openclem.detector import Detector
from openclem.structures import ImageSettings, SerialSettings #, ExposureMode
import numpy as np


class BasleracA1920_155um(Detector):
    def __init__(self):
        self.name = "Basler Detector"
        self.serial_connection = None
        self.camera = None
        self._pixel_size = 5.86e-6
    
    @classmethod
    def __id__(self):
        return "basler"
    
    def connect(self, serial_settings: SerialSettings) -> None:
        try:
            logging.info("Connecting to Basler detector on port: %s", serial_settings.port)
            self.serial_connection = utils.connect_to_serial_port(
                serial_settings=serial_settings
            )
            logging.info("Connected to Basler detector on port: %s", serial_settings.port)
        except Exception as e:
            logging.error("Could not connect to Basler detector on port: %s", serial_settings.port)
            logging.error(e)

    def disconnect(self):
        if self.serial_connection is not None:
            try:
                logging.info("Disconnecting from Basler detector")
                self.serial_connection.close()
                logging.info("Disconnected from Basler detector")
            except Exception as e:
                logging.error("Could not disconnect from Basler detector")
                logging.error(e)
        else:
            logging.info("No Basler detector to disconnect from")

    def init_camera(self):
        try:
            self.camera = pylon.InstantCamera(
                pylon.TlFactory.GetInstance().CreateFirstDevice()
            )
        except Exception as e:
            logging.error("Could not initialize Basler camera")
            logging.error(e)

    def open_camera(self):
        if self.camera is not None:
            try:
                self.camera.Open()
            except Exception as e:
                logging.error("Could not open Basler camera")
                logging.error(e)

    def close_camera(self):
        if self.camera is not None:
            try:
                self.camera.Close()
            except Exception as e:
                logging.error("Could not close Basler camera")
                logging.error(e)

    def grab_image(self, image_settings: ImageSettings = None) -> np.ndarray:
        if self.camera is None or image_settings is None: return
        try:
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

        except Exception as e:
            if self.camera is not None:
                self.camera.Close()
            logging.error("Could not grab image from Basler camera")
            logging.error(e)

    @property
    def exposure_time(self):
        try:
            return self.camera.ExposureTime.GetValue()
        except Exception as e:
            try:
                return self.camera.ExposureTimeAbs.GetValue()
            except Exception as e:
                if self.camera is not None:
                    self.camera.Close()
                logging.error("Could not get exposure time from Basler camera")
                logging.error(e)

    @exposure_time.setter
    def exposure_time(self, exposure_time: float = None):
        if exposure_time is None:
            return
        try:
            self.camera.ExposureTime.SetValue(exposure_time)
        except Exception as e:
            try:
                self.camera.ExposureTimeAbs.SetValue(exposure_time)
            except Exception as e:
                if self.camera is not None:
                    self.camera.Close()
                logging.error("Could not set exposure time on Basler camera")
                logging.error(e)

    # @property
    # def exposure_mode(self):
    #     try:
    #         return self.camera.ExposureMode.GetValue()
    #     except Exception as e:
    #         if self.camera is not None:
    #             self.camera.Close()
    #         logging.error("Could not get exposure mode from Basler camera")
    #         logging.error(e)

    # @exposure_mode.setter
    # def exposure_mode(self, exposure_mode: ExposureMode = None):
    #     if exposure_mode is None:
    #         return
    #     try:
    #         if exposure_mode == ExposureMode.TIMED:
    #             self.camera.ExposureMode.SetValue("Timed")
    #         elif exposure_mode == ExposureMode.TRIGGER_WIDTH:
    #             self.camera.ExposureMode.SetValue("TriggerWidth")
    #             self.camera.AcquisitionFrameRateEnable.SetValue(False)
    #     except Exception as e:
    #         self.camera.Close()
    #         logging.error("Could not set exposure mode on Basler camera")
    #         logging.error(e)
    
    @property
    def pixel_size(self):
        return self._pixel_size
    
    @pixel_size.setter
    def pixel_size(self, pixel_size: float = None):
        if pixel_size is None:
            return
        self._pixel_size = pixel_size

import logging

from openclem import utils
from openclem.detector import Detector
from openclem.detectors.hamamatsu.dcam.dcam import *
from openclem.structures import ImageSettings, DetectorSettings, TriggerSource, ExposureMode, TriggerEdge, ImageMode
from queue import Queue


import threading

image_conversion_dict = {
    "exposure_mode": {ExposureMode.TIMED: 1, ExposureMode.TRIGGER_WIDTH: 2},
    "trigger_source": {TriggerSource.INTERNAL: 1, TriggerSource.EXTERNAL: 2, TriggerSource.SOFTWARE: 3},
    "trigger_edge": {TriggerEdge.FALLING: 1, TriggerEdge.RISING: 2},
}


class HamamatsuOrcaFlash4(Detector):
    def __init__(self, detector_settings: DetectorSettings):
        self.settings = detector_settings
        self.name = "Hamamatsu Detector"
        self.serial_connection = None
        self.port = None
        self.camera = None
        self._pixel_size = 6.5e-6
        self._connected = False

    def __repr__(self):
        return f"HamamatsuOrcaFlash4({self.settings})"

    @classmethod
    def __id__(self):
        return "hamamatsu"

    def connect(self) -> None:
        try:
            if Dcamapi.init() is not False:
                self._connected = True
                logging.info("DCAM-API initialized")
        except Exception as e:
            self._connected = False
            logging.error(f"Could not connect to Hamamatsu detector")
            logging.error(e)

    def disconnect(self) -> None:
        if self.port is not None:
            try:
                logging.info("Disconnecting from Hamamatsu detector")
                Dcamapi.uninit()
                logging.info("Disconnected from Hamamatsu detector")
            except Exception as e:
                logging.error("Could not disconnect from Hamamatsu detector")
                logging.error(e)
        else:
            logging.info("No Hamamatsu detector to disconnect from")

    def init_camera(self):

        if self.camera is None:
            self.camera = Dcam(0)
        
        self.open_camera()
           
        self.trigger_source = image_conversion_dict["trigger_source"][self.settings.trigger_source]
        self.trigger_edge = image_conversion_dict["trigger_edge"][self.settings.trigger_edge]
        self.exposure_mode = image_conversion_dict["exposure_mode"][self.settings.exposure_mode]
        
        # logging.info(f"Trigger Source: {self.trigger_source}")
        # logging.info(f"Trigger Edge: {self.trigger_edge}")
        # logging.info(f"Exposure Mode: {self.exposure_mode}")

        dcamerr = self.camera.lasterr()
        logging.info(f"DCAM error: {dcamerr}") 

    def open_camera(self):
        if self.camera is not None:
            try:
                self.camera.dev_open()
            except Exception as e:
                logging.error("Could not open Hamamatsu camera")
                logging.error(e)

    def close_camera(self):
        if self.camera is not None:
            try:
                self.camera.dev_close()
            except Exception as e:
                logging.error("Could not close Hamamatsu camera")
                logging.error(e)

    def grab_image(self, image_settings: ImageSettings, image_queue: Queue, stop_event: threading.Event):
        import time
        
        if self.camera:
            if not self.camera.is_opened():
                self.open_camera()
        else:
            logging.info("Camera not available")
            return

        count = image_settings.n_images
        count_ = 1
            
        self.camera.buf_alloc(count)
        self.camera.cap_start()

        try:    
            while count_ <= count and not stop_event.is_set():
                # logging.info(f"Capturing image {count_} of {count}")
                
                if self.settings.trigger_source == TriggerSource.SOFTWARE:
                    self.camera.cap_firetrigger()
                
                
                if self.camera.wait_capevent_frameready(timeout_millisec=self.settings.timeout) is not False:
                    image = np.array(self.camera.buf_getlastframedata()).T
                    
                    if image_queue:
                        image_queue.put(image)
                        # logging.info(f"Putting image {count_} in queue: {image.shape}, {np.mean(image)}")
                    
                    if image_settings.mode is ImageMode.SINGLE:
                        count_ += 1
                else:
                    dcamerr = self.camera.lasterr()
                    if dcamerr.is_timeout():
                        logging.error("Timeout error")
                        break
                    else:
                        logging.error("Error: %s", dcamerr)

                # logging.info(f"Captured image {count_} of {count}")
                # logging.info(f"Stop event is set: {stop_event.is_set()}")

        except Exception as e:
            logging.error("Could not grab image")
            logging.error(e)
        finally:
            logging.info("Stopping camera capture")
            logging.info(f"Dcamapi error: {self.camera.lasterr()}") # map it to actuall error message
            self.camera.cap_stop()
            logging.info("Releasing camera buffer")
            self.camera.buf_release()
            logging.info("Closing camera")
            self.close_camera()
            stop_event.set()

    # TODO: fix the bug in these properites, crashes after getting, but only in ui
    @property
    def exposure_time(self):
        try:
            return self.camera.prop_getvalue(DCAM_IDPROP.EXPOSURETIME)

        except Exception as e:
            logging.error("Could not get exposure time")
            logging.error(e)

    @exposure_time.setter
    def exposure_time(self, value):
        try:
            self.camera.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, value)
        except Exception as e:
            logging.error("Could not set exposure time")
            logging.error(e)

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        self._pixel_size = value

    @property
    def exposure_mode(self):
        try:
            return self.camera.prop_getvaluetext(
                DCAM_IDPROP.TRIGGERACTIVE,
                self.camera.prop_getvalue(DCAM_IDPROP.TRIGGERACTIVE),
            )
        except Exception as e:
            logging.error("Could not get exposure mode")
            logging.error(e)

    @exposure_mode.setter
    def exposure_mode(self, value):
        try:
            self.camera.prop_setvalue(DCAM_IDPROP.TRIGGERACTIVE, value)
        except Exception as e:
            logging.error("Could not set exposure mode")
            logging.error(e)

    @property
    def trigger_source(self):
        try:
            return self.camera.prop_getvaluetext(
                DCAM_IDPROP.TRIGGERSOURCE,
                self.camera.prop_getvalue(DCAM_IDPROP.TRIGGERSOURCE),
            )
        except Exception as e:
            logging.error("Could not get trigger source")
            logging.error(e)

    @trigger_source.setter
    def trigger_source(self, value):
        try:
            self.camera.prop_setvalue(DCAM_IDPROP.TRIGGERSOURCE, value)
        except Exception as e:
            logging.error("Could not set trigger source")
            logging.error(e)

    @property
    def trigger_edge(self):
        try:
            return self.camera.prop_getvaluetext(
                DCAM_IDPROP.TRIGGERPOLARITY,
                self.camera.prop_getvalue(DCAM_IDPROP.TRIGGERPOLARITY),
            )
        except Exception as e:
            logging.error("Could not get trigger edge")
            logging.error(e)

    @trigger_edge.setter
    def trigger_edge(self, value):
        try:
            self.camera.prop_setvalue(DCAM_IDPROP.TRIGGERPOLARITY, value)
        except Exception as e:
            logging.error("Could not set trigger edge")
            logging.error(e)

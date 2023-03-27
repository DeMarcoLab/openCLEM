import logging

from openclem import utils
from openclem.detector import Detector
from openclem.detectors.hamamatsu.dcam.dcam import *
from openclem.structures import ImageSettings, DetectorSettings

image_conversion_dict = {
    "exposure_mode": {"edge": 1, "level": 2},
    "trigger_source": {"internal": 1, "external": 2, "software": 3},
    "trigger_edge": {"falling": 1, "rising": 2},
}


class HamamatsuOrcaFlash4(Detector):
    def __init__(self, detector_settings: DetectorSettings):
        self.settings = detector_settings
        self.name = "Hamamatsu Detector"
        self.serial_connection = None
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
        try:
            if not self._connected:
                self.connect()
            self.camera = Dcam(0)
            logging.info("Hamamatsu camera initialized")
        except Exception as e:
            logging.error("Could not initialize Hamamatsu camera")
            logging.error(e)

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

    def grab_image(self, image_settings: ImageSettings = None) -> np.ndarray:
        try:
            self.camera.dev_close()
            self.camera = Dcam(0)
            self.camera.dev_open()
                
            self.exposure_time = image_settings.exposure
            self.trigger_source = image_conversion_dict["trigger_source"][image_settings.trigger_source]
            self.trigger_edge = image_conversion_dict["trigger_edge"][image_settings.trigger_edge]
            self.exposure_mode = image_conversion_dict["exposure_mode"][image_settings.exposure_mode]
            self.camera.prop_setvalue(DCAM_IDPROP.TRIGGER_MODE, 1)
            count = image_settings.n_images
            count_ = 0
            images = []
            if self.camera.buf_alloc(count) is not False:
                if self.camera.cap_start() is not False:
                    while count_ < count:
                        if image_settings.trigger_source == "software":
                            self.camera.cap_firetrigger()
                        if self.camera.wait_capevent_frameready(timeout_millisec=image_settings.timeout) is not False:
                            images.append(np.array(self.camera.buf_getlastframedata()).T)
                            count_ += 1
                        else:
                            dcamerr = self.camera.lasterr()
                            if dcamerr.is_timeout():
                                logging.error("Timeout error")
                                break
                            else:
                                logging.error("Error: %s", dcamerr)

                    self.camera.cap_stop()
                    self.camera.buf_release()
                    self.close_camera()
                    return images
                self.camera.buf_release()

        except Exception as e:
            logging.error("Could not grab image")
            logging.error(e)

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

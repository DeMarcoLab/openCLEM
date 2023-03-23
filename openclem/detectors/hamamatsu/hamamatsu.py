import logging

from openclem import utils
from openclem.detector import Detector
from openclem.detectors.hamamatsu.dcam.dcam import *
from openclem.structures import ImageSettings, SerialSettings


class HamamatsuOrcaFlash4(Detector):
    def __init__(self):
        self.name = "Hamamatsu Detector"
        self.serial_connection = None
        self.camera = None
        self._pixel_size = 6.5e-6 

    @classmethod
    def __id__(self):
        return "hamamatsu"

    def connect(self, serial_settings: SerialSettings) -> None:
        try:
            logging.info("Connecting to Hamamatsu detector on port: %s", serial_settings.port)
            self.serial_connection = utils.connect_to_serial_port(
                serial_settings=serial_settings
            )
            logging.info("Connected to Hamamatsu detector on port: %s", serial_settings.port)
        except Exception as e:
            logging.error("Could not connect to Hamamatsu detector on port: %s", serial_settings.port)
            logging.error(e)

    def disconnect(self) -> None:
        if self.serial_port is not None:
            try:
                logging.info("Disconnecting from Hamamatsu detector")
                self.serial_connection.close()
                logging.info("Disconnected from Hamamatsu detector")
            except Exception as e:
                logging.error("Could not disconnect from Hamamatsu detector")
                logging.error(e)
        else:
            logging.info("No Hamamatsu detector to disconnect from")

    def init_camera(self):  
        try:    
            if Dcamapi.init() is not False:
                print("DCAM-API initialized")
                self.camera = Dcam(0)
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
        if self.camera is None or image_settings is None: return
        try:
            self.open_camera()
            self.camera.cap_stop()
            self.camera.buf_alloc(1)

            self.exposure_time = image_settings.exposure

            if self.camera.cap_start() is not False:
                while True:
                    if self.camera.wait_capevent_frameready(2000) is not False:
                        data = self.camera.buf_getframe(0)
                        break

                    dcamerr = self.camera.lasterr()
                    if dcamerr.is_timeout():
                        logging.error("Timeout error")
                        break
                    else:
                        logging.error("Error: %s", dcamerr.message())
                
                self.camera.cap_stop()
                self.camera.buf_release()
                image = np.array(data[-1]).T
                self.close_camera()
                return image
            
        except Exception as e:
            logging.error("Could not grab image")

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
            return self.camera.prop_getvalue(DCAM_IDPROP.TRIGGER_MODE)
        except Exception as e:
            logging.error("Could not get trigger mode")
            logging.error(e)

    @exposure_mode.setter
    def exposure_mode(self, value):
        try:
            self.camera.prop_setvalue(DCAM_IDPROP.TRIGGER_MODE, value)
        except Exception as e:
            logging.error("Could not set trigger mode")
            logging.error(e)

    
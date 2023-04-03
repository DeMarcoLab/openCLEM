from openclem import utils
from openclem.structures import SynchroniserMessage, SynchroniserSettings
from openclem.synchronisation import Synchroniser
import time
import logging

MODE_CONVERSION = {
    "single": "S",
    "live": "L",
    "volume": "V",
}

class DemoSynchroniser(Synchroniser):
    def __init__(self, synchroniser_settings: SynchroniserSettings):
        self.settings = synchroniser_settings
        self.name = synchroniser_settings.name
        self.pins = {}
        self.serial_connection = None

    def connect(self):
        self.serial_connection = "Serial Connection"

    def disconnect(self):
        if self.serial_connection is not None:
            logging.info(f"Closing serial connection {self.serial_connection}")

    def send_command(self, command):
        if self.serial_connection is None: return

        logging.info(f"Sending command {command}")
        return "Response"

    def sync_image(self, message: SynchroniserMessage):
        exposure_string = ""
        exposures = message.exposures
        edge = message.trigger_edge
        for exposure in exposures:
            exposure_string += f"{exposure} "
        n_slices = message.n_slices
        mode = MODE_CONVERSION[message.mode.value]
        command = f"E{mode}{exposure_string}{n_slices} {edge.value}"
        self.send_command(command)
        return command

    def stop_sync(self):
        command = "E_STOP"
        logging.info(f"Sending command {command}")
        self.send_command(command)
        return command
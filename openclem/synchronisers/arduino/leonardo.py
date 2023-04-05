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

class ArduinoLeonardo(Synchroniser):
    def __init__(self, synchroniser_settings: SynchroniserSettings):
        self.settings = synchroniser_settings
        self.name = synchroniser_settings.name
        self.pins = {}
        self.serial_connection = None

    def connect(self):
        logging.info(f"Connecting to Arduino Leonardo synchroniser {self.name}.")
        self.serial_connection = utils.connect_to_serial_port(self.settings.connection.settings)
        time.sleep(1) # required for initialisation
        logging.info(f"Serial connection: {self.serial_connection}.")
        logging.info(f"Connected to Arduino Leonardo synchroniser {self.name}.")

    def disconnect(self):
        if self.serial_connection is not None:
            self.stop_sync()
            self.serial_connection.close()

    def send_command(self, command):
        if self.serial_connection is None: return

        if not self.serial_connection.is_open:
            self.serial_connection.open()
            time.sleep(1) # required for initialisation
        response = utils.write_serial_command(self.serial_connection, command, check=True)
        logging.info(f"Arduino Leonardo response: {response}.")
        return response

    def sync_image(self, message: SynchroniserMessage):
        exposure_string = ""
        exposures = message.exposures
        edge = message.trigger_edge
        for exposure in exposures:
            exposure_string += f"{exposure} "
        n_slices = message.n_slices
        mode = MODE_CONVERSION[message.mode.value]
        command = f"E{mode}{exposure_string}{n_slices} {edge.value}"
        logging.info(f"Arduino Leonardo command: {command}.")
        self.send_command(command)
        return command

    def stop_sync(self):
        command = "E_STOP"
        self.send_command(command)
        return command

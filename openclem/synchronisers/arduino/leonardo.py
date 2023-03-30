from openclem import utils
from openclem.structures import SynchroniserMessage, SynchroniserSettings
from openclem.synchronisation import Synchroniser
import time

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
        self.serial_connection = utils.connect_to_serial_port(self.settings.serial_settings)

    def disconnect(self):
        if self.serial_connection is not None:
            self.serial_connection.close()

    def send_command(self, command):
        if self.serial_connection is None: return

        if not self.serial_connection.is_open:
            self.serial_connection.open()
            time.sleep(1) # required for initialisation
        response = utils.write_serial_command(self.serial_connection, command, check=True)
        return response

    def sync_image(self, message: SynchroniserMessage):
        exposure_string = ""
        exposures = message.exposures
        edge = message.trigger_edge
        for exposure in exposures:
            exposure_string += f"{exposure} "
        n_slices = message.n_slices
        mode = MODE_CONVERSION[message.mode]
        command = f"E{mode}{exposure_string}{n_slices} {edge.value}"
        self.send_command(command)
        return command

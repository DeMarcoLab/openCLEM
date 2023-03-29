from openclem import utils
from openclem.structures import SynchroniserMessage, SynchroniserSettings
from openclem.synchronisation import Synchroniser

MODE_CONVERSION = {
    "single": "S",
    "live": "L",
    "volume": "V",
}

class ArduinoLeonardo(Synchroniser):
    def __init__(self, synchroniser_settings: SynchroniserSettings):
        self.settings = synchroniser_settings
        self.pins = {}
        self.serial_connection = None

    def connect(self):
        self.serial_connection = utils.connect_to_serial_port(self.settings.serial_settings)

    def disconnect(self):
        if self.serial_connection is not None:
            self.serial_connection.close()

    def send_command(self, command):
        if self.serial_connection is None: return

        self.serial_connection.close()
        self.serial_connection.open()
        # TODO: investigate whether sleep(1) is required here
        utils.write_serial_command(self.serial_connection, command)
        self.serial_connection.close()

    def synch_image(self, message: SynchroniserMessage):
        exposure_string = ""
        exposures = message.exposures
        for exposure in exposures:
            exposure_string += f"{exposure} " 
        n_slices = message.n_slices
        mode = MODE_CONVERSION[message.mode]
        command = f"E{mode}{exposure_string}{n_slices}"
        self.send_command(command)
        return command
    
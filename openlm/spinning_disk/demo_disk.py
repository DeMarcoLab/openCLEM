from openlm.structures import SerialSettings
from openlm import utils
import logging

# For piedisc, the positions are:
# Disk: 1
# Emission filter: 2
# Dichroic: 1

class DemoDisk:

    def __init__(self):
        self.connection = None

    def connect(self):
        serial_settings_dict = {
            'port': 'COM6',
            'baudrate': 9600,
            'timeout': 1,
        }
        serial_settings = SerialSettings.__from_dict__(serial_settings_dict)
        self.connection = "DemoConnection"
        logging.info(f"DemoDisk - {self.connection} connected")
    
    def disconnect(self):
        logging.info(f"DemoDisk - {self.connection} disconnected")
        self.connection = None

    def disk_position(self, position: int):
        """moves the spinning disk to the given position

        Args:
            position (int): position of the disk
            options:
                0: disk out
                1: disk in to 70um
                2: disk in to 40um
        """
        if position not in [0, 1, 2]:
            raise ValueError('position must be 0, 1 or 2')
        logging.info(f"Moving disk to position: {position}")

    def disk_onoff(self, onoff: int):
        """turns the disk on or off

        Args:
            onoff (int): 0 or 1
            options:
                0: disk off
                1: disk on
        """
        if onoff not in [0, 1]:
            raise ValueError('onoff must be 0 or 1')
        logging.info(f"Turning disk on/off: {onoff}")

    def get_status(self):
        """gets the status of the xlight"""

        
        return f"DemoDisk - {self.connection} status"

    def emission_filter(self, position):
        """moves the emission filter to the given position

        Args:
            position (int): position of the emission filter
            options:
                1-8: filter position 1-8
        """
        if position not in range(1, 9):
            raise ValueError('position must be 1-8')
        logging.info(f"Moving emission filter to position: {position}")

    def dichroic(self, position):
        """moves the dichroic to the given position

        Args:
            position (int): position of the dichroic
            options:
                1-5: dichroic position 1-5
        """
        if position not in range(1, 6):
            raise ValueError('position must be 1-5')
        logging.info(f"Moving dichroic to position: {position}")

    def home(self):
        """homes the disk"""
        
        logging.info(f"Homing DemoDisk")
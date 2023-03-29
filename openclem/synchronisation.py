from abc import ABC, abstractmethod

from openclem.structures import SynchroniserSettings


class Synchroniser(ABC):
    def __init__(self, synchroniser_settings: SynchroniserSettings):
        self.settings = synchroniser_settings
        self.pins = {}
        self.serial_connection = None

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send_command(self, command):
        pass

    @abstractmethod
    def synch_image(self, message):
        pass

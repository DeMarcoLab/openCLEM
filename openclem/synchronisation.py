from abc import ABC, abstractmethod

from openclem.structures import SynchroniserSettings


class Synchroniser(ABC):
    def __init__(self, synchroniser_settings: SynchroniserSettings):
        self.settings = synchroniser_settings
        self.name = synchroniser_settings.name
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
    def sync_image(self, message):
        pass

    def __repr__(self) -> str:
        return f"Synchroniser {self.name}"
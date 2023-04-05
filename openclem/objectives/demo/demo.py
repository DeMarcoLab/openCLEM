
from openclem.objective import ObjectiveStage
from openclem.structures import ObjectiveSettings
import logging


class DemoObjectiveStage(ObjectiveStage):
    def __init__(self, objective_settings: ObjectiveSettings):
        self.name = objective_settings.name
        # self.connection = objective_settings.connection
        self.settings = objective_settings
        self._position = 0.0
        self.saved_position = None
    
    def connect(self):
        logging.info(f"Connecting to {self.name} objective")
        logging.info(f"Socket settings: {self.settings.connection}")
    
    def disconnect(self):
        logging.info(f"Disconnecting from {self.name} objective")
    
    def initialise(self):
        logging.info(f"Initialising {self.name} objective")

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def save_position(self, position: float) -> None:
        self.saved_position = position

    def relative_move(self, distance: float) -> None:
        self.position += distance

    def absolute_move(self, position: float) -> None:
        self.position = position

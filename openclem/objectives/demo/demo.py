
from openclem.objective import Objective

class DemoObjective(Objective):
    def __init__(self, name:str):
        self.name = name
        self._position = 0.0
        self.saved_position = None
    
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

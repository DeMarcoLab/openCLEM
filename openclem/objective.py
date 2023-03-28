from abc import ABC, abstractmethod

class Objective(ABC):
    def __init__(self, name: str):
        self.name = name
        self.position = 0
        self.saved_position = None
        self.connection = None

    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    

    @abstractmethod
    def initialise(self):
        pass

    @property
    @abstractmethod
    def position(self) -> float:
        pass

    @position.setter
    @abstractmethod
    def position(self, value:float):
        pass

    def save_position(self, position: float) -> None:
        pass

    @abstractmethod    
    def relative_move(self, distance: float) -> None:
        pass
    
    @abstractmethod
    def absolute_move(self, position: float):
        pass


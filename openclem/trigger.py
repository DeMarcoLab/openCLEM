from abc import ABC, abstractmethod


class Trigger(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def check(self, state):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
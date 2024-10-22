from abc import ABC, abstractmethod


class BaseEncoder(ABC):

    @abstractmethod
    def encode(self, **input_data: dict):
        pass

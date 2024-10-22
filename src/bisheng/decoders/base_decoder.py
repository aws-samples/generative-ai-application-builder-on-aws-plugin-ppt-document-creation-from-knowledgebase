from abc import ABC, abstractmethod


class BaseDecoder(ABC):

    @abstractmethod
    def decode(self, **input_data: dict):
        pass

    @abstractmethod
    def get_encoder_metadata(self) -> dict:
        pass

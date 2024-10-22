from abc import ABC, abstractmethod


class BasePromptTemplate(ABC):

    @classmethod
    def get_required_params(cls) -> set:
        return set()

    def __init__(self, **kwargs):
        required_params = self.get_required_params()
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        self.__dict__.update(kwargs)

    @abstractmethod
    def create_instruction(self, **input_data) -> str:
        pass

from abc import ABC, abstractmethod


class BasePrompt(ABC):

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def get_instruction_prompt(self) -> str:
        pass

    @abstractmethod
    def to_json(self):
        pass

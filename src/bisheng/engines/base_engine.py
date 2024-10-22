from abc import ABC, abstractmethod

from bisheng.prompting.base_prompt import BasePrompt
from bisheng.prompting.base_response import BaseResponse


class BaseEngine(ABC):

    @abstractmethod
    def invoke(self, prompt: BasePrompt) -> BaseResponse:
        pass

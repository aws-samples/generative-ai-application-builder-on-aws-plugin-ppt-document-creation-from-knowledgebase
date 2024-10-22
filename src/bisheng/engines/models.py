from abc import ABC
from enum import Enum


class Model(ABC, Enum):

    def get_request_body(self):
        pass


class Claude3Sonnet(Model):

    def get_request_body(self):
        return {"anthropic_version": self._version, "max_tokens": self._hyperparameters["max_tokens"],
                "system": prompt.get_system_prompt(), "messages": [{
                "role": self._hyperparameters["role"],
                "content": [{"type": "text", "text": prompt.get_instruction_prompt()}, ],
            }], "temperature": self._hyperparameters["temperature"],
                "top_p": self._hyperparameters["top_p"],
                "top_k": self._hyperparameters["top_k"]
                }

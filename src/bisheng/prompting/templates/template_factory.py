from enum import Enum

from pydantic import BaseModel

from bisheng.prompting.templates.prompt_templates import BasePromptTemplate, GaabWithKnowledgeBasePromptTemplate
from bisheng.prompting.templates.prompt_templates import (
    OneShotWithContextPromptTemplate
)
from bisheng.utils import import_class

_DRIVER_MAP = {
    "one-shot-with-context": OneShotWithContextPromptTemplate,
    "gaab-with-knowledge-base": GaabWithKnowledgeBasePromptTemplate
}


class TemplateFactory(BaseModel):

    config: dict

    def create(self):
        driver_cls = self._get_driver_class()

        return driver_cls

    def _get_driver_class(self) -> type[BasePromptTemplate]:
        if self.config["type"] in _DRIVER_MAP:
            driver_cls = _DRIVER_MAP[self.config["type"]]
        else:
            driver_cls = import_class(self.config["type"], parent_class=BasePromptTemplate)
        return driver_cls

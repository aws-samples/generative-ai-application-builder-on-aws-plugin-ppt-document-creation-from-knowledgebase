from pydantic import BaseModel
from bisheng.engines import BaseEngine
from bisheng.engines.bedrock import BedrockEngine
from bisheng.engines.gaab import GaabStreamingEngine
from bisheng.utils import import_class

_DRIVER_MAP = {
    "bedrock": BedrockEngine,
    "gaab": GaabStreamingEngine
}


class EngineFactory(BaseModel):

    config: dict

    def create(self):
        driver_cls = self._get_driver_class()
        driver_cls = driver_cls(**{k: v for k, v in self.config.items() if k != "type"})
        return driver_cls

    def _get_driver_class(self) -> type[BaseEngine]:
        if self.config["type"] in _DRIVER_MAP:
            driver_cls = _DRIVER_MAP[self.config["type"]]
        else:
            driver_cls = import_class(self.config["type"], parent_class=BaseEngine)
        return driver_cls

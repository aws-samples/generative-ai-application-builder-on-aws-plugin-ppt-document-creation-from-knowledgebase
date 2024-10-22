from pydantic import BaseModel

from bisheng.encoders.base_encoder import BaseEncoder
from bisheng.encoders.pptx_encoder import PptxEncoder
from bisheng.encoders.transparency_report_encoder import TransparencyReportEncoder
from bisheng.utils import import_class

_ENCODER_MAP = {
    "transparency-report": TransparencyReportEncoder,
    "pptx":  PptxEncoder,
}


class EncoderFactory(BaseModel):
    config: list[dict]

    def create(self, encoder_config: dict) -> BaseEncoder:
        driver_cls = self._get_encoder_class(encoder_config)

        return driver_cls(**{k: v for k, v in encoder_config.items() if k != "type"})

    def _get_encoder_class(self, encoder_config) -> type[BaseEncoder]:
        if encoder_config["type"] in _ENCODER_MAP:
            driver_cls = _ENCODER_MAP[encoder_config["type"]]
        else:
            driver_cls = import_class(encoder_config["type"], parent_class=BaseEncoder)
        return driver_cls

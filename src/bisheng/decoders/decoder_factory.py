from pydantic import BaseModel

from bisheng.decoders.base_decoder import BaseDecoder
from bisheng.decoders.pptx_decoder import PptxDecoder
from bisheng.utils import import_class

_DECODER_MAP = {
    "one-shot-pptx-with-context": PptxDecoder,
    "pptx": PptxDecoder,
}


class DecoderFactory(BaseModel):
    config: dict

    def create(self):
        driver_cls = self._get_decoder_class()

        decoder = driver_cls(**{k: v for k, v in self.config.items() if k != "type" and k != "decorators"})

        return decoder

    def _get_decoder_class(self) -> type[BaseDecoder]:
        if self.config["type"] in _DECODER_MAP:
            driver_cls = _DECODER_MAP[self.config["type"]]
        else:
            driver_cls = import_class(self.config["type"], parent_class=BaseDecoder)
        return driver_cls

# from bisheng.decoders.pptx_decoder import PptxDecoder
# from src.bisheng.decoders import decoder_factory
# import pytest
#
#
# @pytest.fixture
# def target_decoder_factory_fixture_pptx_decoder():
#     return decoder_factory.DecoderFactory(
#         config={"type": "one-shot-pptx-with-context"}
#     )
#
#
# _one_shot_pptx_with_context_config = {"type": "one-shot-pptx-with-context"}

import pytest
from unittest.mock import patch, MagicMock
from src.bisheng.decoders.decoder_factory import DecoderFactory, PptxDecoder, BaseDecoder


# Test case for creating a known decoder type
def test_create_known_decoder(tmp_path):
    config = {
        "type": "pptx",
        "prompts_path": tmp_path,
        "shots_path": tmp_path,
        "context_path": tmp_path,
        "instruction": "test"
    }
    factory = DecoderFactory(config=config)
    decoder = factory.create()

    assert isinstance(decoder, PptxDecoder)


# Test case for creating an unknown decoder type
def test_create_unknown_decoder():
    with patch('bisheng.decoders.decoder_factory.import_class') as mock_import:
        mock_decoder = MagicMock(spec=BaseDecoder)
        mock_import.return_value = mock_decoder

        config = {"type": "custom_decoder", "custom_option": "custom_value"}
        factory = DecoderFactory(config=config)
        decoder = factory.create()

        mock_import.assert_called_once_with("custom_decoder", parent_class=BaseDecoder)
        assert isinstance(decoder, MagicMock)
        mock_decoder.assert_called_once_with(custom_option="custom_value")


# Test case for creating a decoder with multiple options
def test_create_decoder_with_multiple_options():
    config = {
        "type": "one-shot-pptx-with-context",
        "option1": "value1",
        "option2": "value2",
        "decorators": ["some_decorator"]
    }
    factory = DecoderFactory(config=config)
    decoder = factory.create()

    assert isinstance(decoder, PptxDecoder)
    assert decoder.option1 == "value1"
    assert decoder.option2 == "value2"
    assert not hasattr(decoder, "decorators")  # Ensure 'decorators' is not passed to the decoder


# Test case for handling invalid decoder type
def test_invalid_decoder_type():
    with pytest.raises(ImportError):
        config = {"type": "non_existent_decoder"}
        factory = DecoderFactory(config=config)
        factory.create()


# Test case for empty config
def test_empty_config():
    with pytest.raises(KeyError):
        config = {}
        factory = DecoderFactory(config=config)
        factory.create()


# Test case for config with only type
def test_config_with_only_type():
    config = {"type": "pptx"}
    factory = DecoderFactory(config=config)
    decoder = factory.create()

    assert isinstance(decoder, PptxDecoder)
    assert not hasattr(decoder, "type")  # Ensure 'type' is not passed to the decoder


# Test case for creating different known decoder types
@pytest.mark.parametrize("decoder_type", ["one-shot-pptx-with-context", "pptx"])
def test_create_different_known_decoders(decoder_type):
    config = {"type": decoder_type}
    factory = DecoderFactory(config=config)
    decoder = factory.create()

    assert isinstance(decoder, PptxDecoder)


# class TestDecoderFactory:
#
#     def test_get_decoder_class_one_shot_pptx_with_context(self):
#         factory = decoder_factory.DecoderFactory(
#             config=_one_shot_pptx_with_context_config
#         )
#         assert PptxDecoder in factory._get_decoder_class().mro()
#
#     def test_create(self, mocker, target_decoder_factory_fixture_pptx_decoder):
#         mock_get_evaluator_class = mocker.patch.object(
#             target_decoder_factory_fixture_pptx_decoder, "_get_decoder_class"
#         )
#
#         mock_evaluator_cls = mocker.patch.object(
#             decoder_factory, decoder_factory._DECODER_MAP["one-shot-pptx-with-context"].__name__
#         )
#         mock_get_evaluator_class.return_value = mock_evaluator_cls
#
#         target_decoder_factory_fixture_pptx_decoder.create()
#
#         mock_evaluator_cls.assert_called_once_with()
#



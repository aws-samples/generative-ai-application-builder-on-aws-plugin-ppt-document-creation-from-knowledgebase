from bisheng.encoders.pptx_encoder import PptxEncoder
from bisheng.encoders.transparency_report_encoder import TransparencyReportEncoder
from src.bisheng.encoders import encoder_factory
import pytest


@pytest.fixture
def target_encoder_factory_fixture_transparency_report():
    return encoder_factory.EncoderFactory(
        config=[_transparency_report_config]
    )


@pytest.fixture
def target_encoder_factory_fixture_pptx():
    return encoder_factory.EncoderFactory(
        config=[_pptx_config]
    )


_transparency_report_config = {"type": "transparency-report"}
_pptx_config = {"type": "pptx"}


class TestEncoderFactory:

    def test_get_encoder_class_pptx(self):
        factory = encoder_factory.EncoderFactory(
            config=[_pptx_config]
        )
        assert PptxEncoder in factory._get_encoder_class(_pptx_config).mro()

    def test_get_encoder_class_transparency_report(self):
        factory = encoder_factory.EncoderFactory(
            config=[_transparency_report_config]
        )
        assert TransparencyReportEncoder in factory._get_encoder_class(_transparency_report_config).mro()

    def test_create_transparency_report(self, mocker, target_encoder_factory_fixture_transparency_report):
        mock_get_encoder_class = mocker.patch.object(
            target_encoder_factory_fixture_transparency_report, "_get_encoder_class"
        )
        mock_evaluator_cls = mocker.patch.object(
            encoder_factory, encoder_factory._ENCODER_MAP["transparency-report"].__name__
        )
        mock_get_encoder_class.return_value = mock_evaluator_cls
        target_encoder_factory_fixture_transparency_report.create({})
        mock_evaluator_cls.assert_called_once_with()

    def test_create_pptx(self, mocker, target_encoder_factory_fixture_pptx):
        mock_get_encoder_class = mocker.patch.object(
            target_encoder_factory_fixture_pptx, "_get_encoder_class"
        )
        mock_evaluator_cls = mocker.patch.object(
            encoder_factory, encoder_factory._ENCODER_MAP["pptx"].__name__
        )
        mock_get_encoder_class.return_value = mock_evaluator_cls
        target_encoder_factory_fixture_pptx.create({})
        mock_evaluator_cls.assert_called_once_with()

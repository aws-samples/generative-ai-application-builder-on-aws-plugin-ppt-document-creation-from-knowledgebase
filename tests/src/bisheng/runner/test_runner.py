import os
from unittest.mock import patch, mock_open

import pytest
import yaml
from src.bisheng.runner import Runner
from src.bisheng.utils.defaults import CONFIG_FILE_NAME, MAX_NUM_THREADS


@pytest.fixture
def mock_config():
    return {"key": "value"}


@pytest.fixture
def mock_getcwd():
    with patch('os.getcwd') as mock:
        yield mock


@pytest.fixture
def mock_load_yaml():
    with patch('src.bisheng.runner.Runner._load_yaml') as mock:
        yield mock


def test_load_default_directory(mock_load_yaml, mock_getcwd, mock_config):
    mock_getcwd.return_value = "/default/path"
    mock_load_yaml.return_value = mock_config

    runner = Runner.load()

    mock_getcwd.assert_called_once()
    mock_load_yaml.assert_called_once_with(f"/default/path/{CONFIG_FILE_NAME}")
    assert isinstance(runner, Runner)
    assert runner.config == mock_config


def test_load_custom_directory(mock_load_yaml, mock_config):
    custom_dir = "/custom/path"
    mock_load_yaml.return_value = mock_config

    runner = Runner.load(config_dir=custom_dir)

    mock_load_yaml.assert_called_once_with(f"{custom_dir}/{CONFIG_FILE_NAME}")
    assert isinstance(runner, Runner)
    assert runner.config == mock_config


def test_load_file_not_found(mock_load_yaml):
    mock_load_yaml.side_effect = FileNotFoundError

    with pytest.raises(FileNotFoundError):
        Runner.load()


def test_load_invalid_yaml(mock_load_yaml):
    mock_load_yaml.side_effect = yaml.YAMLError

    with pytest.raises(yaml.YAMLError):
        Runner.load()


def test_load_returns_runner_instance(mock_load_yaml, mock_config):
    mock_load_yaml.return_value = mock_config
    result = Runner.load()

    assert isinstance(result, Runner)


def test_init_plan_default_parameters(tmp_path):
    config_path = Runner.init_plan(config_dir=str(tmp_path))

    assert config_path == os.path.join(str(tmp_path), CONFIG_FILE_NAME)
    assert os.path.exists(config_path)


def test_init_plan_custom_parameters(tmp_path):
    custom_filename = "custom_config.yaml"
    config_path = Runner.init_plan(
        config_dir=str(tmp_path),
        debug=True,
        filename=custom_filename
    )

    assert config_path == os.path.join(str(tmp_path), custom_filename)
    assert os.path.exists(config_path)


def test_init_plan_file_already_exists(tmp_path):
    existing_file = tmp_path / CONFIG_FILE_NAME
    existing_file.touch()

    with pytest.raises(FileExistsError):
        Runner.init_plan(config_dir=str(tmp_path))


def test_init_invaled_engine_type(tmp_path):
    with pytest.raises(ValueError):
        Runner.init_plan(config_dir=str(tmp_path), engine_type="test_engine")


def test_init_plan_writes_correct_config(tmp_path):
    config_path = Runner.init_plan(config_dir=str(tmp_path))

    with open(config_path, 'r') as f:
        written_config = yaml.safe_load(f)

    assert "type" in written_config["engine"]
    assert written_config["engine"]["type"] == "bedrock"


def test_init_plan_returns_correct_path(tmp_path):
    expected_path = os.path.join(str(tmp_path), CONFIG_FILE_NAME)
    actual_path = Runner.init_plan(config_dir=str(tmp_path))

    assert actual_path == expected_path


@pytest.mark.parametrize("debug", [True, False])
def test_init_plan_debug_flag(debug, tmp_path):
    Runner.init_plan(config_dir=str(tmp_path), debug=debug)


def test_load_yaml_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            Runner._load_yaml("nonexistent_file.yaml")


def test_load_yaml_invalid_yaml():
    invalid_yaml = "\t{key1: value1\nkey2: : invalid}"

    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        with pytest.raises(yaml.YAMLError):
            Runner._load_yaml("invalid.yaml")


@pytest.fixture
def mock_gaab_config():
    return {"engine": "gaab", "some_gaab_setting": "value"}


@pytest.fixture
def mock_bedrock_config():
    return {"engine": "bedrock", "some_bedrock_setting": "value"}


@pytest.fixture
def mock_generate_gaab(mocker, mock_gaab_config):
    return mocker.patch.object(Runner, '_generate_template_gaab_config', return_value=mock_gaab_config)


@pytest.fixture
def mock_generate_bedrock(mocker, mock_bedrock_config):
    return mocker.patch.object(Runner, '_generate_template_bedrock_config', return_value=mock_bedrock_config)


def test_generate_initial_config_gaab(mock_generate_gaab, mock_generate_bedrock):
    config = Runner.generate_initial_config("gaab")
    assert config == mock_generate_gaab.return_value
    mock_generate_gaab.assert_called_once()
    mock_generate_bedrock.assert_not_called()


def test_generate_initial_config_bedrock(mock_generate_gaab, mock_generate_bedrock):
    config = Runner.generate_initial_config("bedrock")
    assert config == mock_generate_bedrock.return_value
    mock_generate_bedrock.assert_called_once()
    mock_generate_gaab.assert_not_called()


def test_generate_initial_config_invalid_engine(mock_generate_gaab, mock_generate_bedrock):
    with pytest.raises(ValueError) as exc_info:
        Runner.generate_initial_config("invalid_engine")
    assert str(exc_info.value) == "Invalid engine type: invalid_engine"
    mock_generate_gaab.assert_not_called()
    mock_generate_bedrock.assert_not_called()


@pytest.mark.parametrize("engine_type", ["GAAB", "Gaab", "BEDROCK", "Bedrock"])
def test_generate_initial_config_case_sensitivity(engine_type, mock_generate_gaab, mock_generate_bedrock):
    with pytest.raises(ValueError) as exc_info:
        Runner.generate_initial_config(engine_type)
    assert str(exc_info.value) == f"Invalid engine type: {engine_type}"
    mock_generate_gaab.assert_not_called()
    mock_generate_bedrock.assert_not_called()


def test_generate_initial_config_empty_string(mock_generate_gaab, mock_generate_bedrock):
    with pytest.raises(ValueError) as exc_info:
        Runner.generate_initial_config("")
    assert str(exc_info.value) == "Invalid engine type: "
    mock_generate_gaab.assert_not_called()
    mock_generate_bedrock.assert_not_called()


def test_generate_template_gaab_config():
    config = Runner._generate_template_gaab_config()
    assert "engine" in config
    assert config["engine"]["type"] == "gaab"


def test_generate_template_bedrock_config():
    config = Runner._generate_template_bedrock_config()
    assert "engine" in config
    assert config["engine"]["type"] == "bedrock"


def test_resolve_num_threads_with_num_threads_specified():
    assert Runner._resolve_num_threads(num_tests=10, num_threads=5) == 5
    assert Runner._resolve_num_threads(num_tests=3, num_threads=8) == 8
    assert Runner._resolve_num_threads(num_tests=1, num_threads=1) == 1


def test_resolve_num_threads_with_num_threads_none():
    assert Runner._resolve_num_threads(num_tests=10, num_threads=None) == 10
    assert Runner._resolve_num_threads(num_tests=3, num_threads=None) == 3
    assert Runner._resolve_num_threads(num_tests=1, num_threads=MAX_NUM_THREADS) == MAX_NUM_THREADS


def test_resolve_num_threads_with_zero_num_threads():
    assert Runner._resolve_num_threads(num_tests=10, num_threads=0) == 0


def test_resolve_num_threads_with_negative_num_threads():
    assert Runner._resolve_num_threads(num_tests=10, num_threads=-5) == -5


@pytest.mark.parametrize("num_tests, num_threads, expected", [
    (100, None, MAX_NUM_THREADS),
    (2, None, 2),
    (5, 3, 3),
    (1, 10, 10),
    (0, None, 0),
])
def test_resolve_num_threads_parametrized(num_tests, num_threads, expected):
    assert Runner._resolve_num_threads(num_tests, num_threads) == expected

import os
import stat
import uuid

import click
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.bisheng.runner import Runner

from src.bisheng.utils.exceptions import PrintFailureError

from src.bisheng.cli import init, validate_directory, ExitCode
from src.bisheng.utils.defaults import CONFIG_FILE_NAME
from src.bisheng.cli import cli, run


@pytest.fixture
def runner():
    return CliRunner()


def test_init(tmp_path, runner):
    result = runner.invoke(init, [f'--config-dir={tmp_path}', '--debug'])
    assert result.exit_code == 0


def test_init_custom_file_name(tmp_path, runner):
    custom_config = 'test_config.yaml'
    result = runner.invoke(init, [f'--config-dir={tmp_path}', custom_config, '--debug'])
    assert result.exit_code == 0


def test_init_config_file_exists(tmp_path, runner):
    with open(f'{tmp_path}/{CONFIG_FILE_NAME}', 'a'):
        os.utime(f'{tmp_path}/{CONFIG_FILE_NAME}', None)
    result = runner.invoke(init, [f'--config-dir={tmp_path}', '--debug'])
    assert result.exit_code == ExitCode.CONFIG_ALREADY_EXISTS.value


def test_validate_directory_new_directory(tmp_path):
    assert tmp_path == validate_directory({}, "", tmp_path)


def test_validate_directory_raises_is_not_a_directory(tmp_path):
    test_file = f"{tmp_path}/{str(uuid.uuid4())}"
    with open(test_file, 'a'):
        os.utime(test_file, None)
    with pytest.raises(click.BadParameter):
        validate_directory({}, "", test_file)


def test_validate_directory_raises_no_read_permissions(tmp_path):
    current_permissions = os.stat(tmp_path).st_mode
    new_permissions = current_permissions & ~(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    os.chmod(tmp_path, new_permissions)
    with pytest.raises(click.BadParameter):
        validate_directory({}, "", tmp_path)


def test_validate_directory_raises_no_write_permissions(tmp_path):
    current_permissions = os.stat(tmp_path).st_mode
    new_permissions = current_permissions & ~0o222
    os.chmod(tmp_path, new_permissions)
    with pytest.raises(click.BadParameter):
        validate_directory({}, "", tmp_path)


def test_run_command_user_abort(runner):
    with patch('src.bisheng.runner.Runner.load') as mock_load, \
            patch('click.confirm') as mock_confirm:
        mock_load.return_value = MagicMock()
        mock_confirm.return_value = False

        result = runner.invoke(run, ['--config-dir', '/path/to/config'])

        assert result.exit_code != 0


def test_run_command_print_failure(runner, tmp_path):
    with patch('src.bisheng.runner.Runner.load') as mock_load, \
            patch('click.confirm') as mock_confirm, \
            patch('src.bisheng.runner.Runner.run') as mock_run:
        mock_load.return_value = MagicMock()
        mock_confirm.return_value = True
        mock_run.side_effect = PrintFailureError("")

        result = runner.invoke(run, ['--config-dir', tmp_path])

        assert result.exit_code == 1


def test_run_command_missing_config_dir(runner):
    result = runner.invoke(run)
    assert result.exit_code != 0
    assert "Missing option '--config-dir'" in result.output


@patch('src.bisheng.cli.validate_directory')
def test_run_command_invalid_directory(mock_validate, runner, tmp_path):
    mock_validate.side_effect = click.BadParameter("Invalid directory")
    result = runner.invoke(run, ['--config-dir', tmp_path])
    assert result.exit_code != 0

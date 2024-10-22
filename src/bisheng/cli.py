import os
from enum import Enum
from typing import Optional

import click

from bisheng.utils.exceptions import PrintFailureError
from bisheng.runner import Runner
from bisheng.utils.defaults import CONFIG_FILE_NAME


class ExitCode(Enum):
    CONFIG_ALREADY_EXISTS = 1


def validate_directory(ctx, param, value):
    if value:
        if not os.path.isdir(value):
            raise click.BadParameter(f"{value} is not a directory")
        if not os.access(value, os.R_OK) or not os.access(value, os.W_OK):
            raise click.BadParameter(f"No read/write permissions for {value}")
    return value


@click.group()
def cli():
    """
    Exists to create the cli command group.

    :return:
    """
    pass


@cli.command(help="Initialize a YAML config.")
@click.option(
    '--debug',
    is_flag=True,
    type=bool,
    required=False,
    default=False,
    help="Enables debug mode."
)
@click.option(
    "--config-dir",
    type=str,
    metavar='<PATH>',
    required=True,
    help="The directory location of the config yaml file.",
    callback=validate_directory
)
@click.option(
    "--engine-type",
    type=click.Choice(['bedrock', 'gaab']),
    required=False,
    default='bedrock',
    metavar='<ENGINE_TYPE>',
    help="The engine type to use. Valid options are 'bedrock' or 'gaab'"
)
@click.argument(
    'filename',
    type=str,
    metavar='<FILENAME>',
    required=False,
    default=CONFIG_FILE_NAME
)
def init(config_dir, engine_type, debug, filename):
    """Initialize Bisheng config FILENAME at the specified PATH.

    CONFIG_DIR is the name of the directory where the config file will be created. This is required.
    ENGINE_TYPE is the type of engine to use. Defaults to bedrock.
    FILENAME is the name of the config file. Defaults to bisheng.yaml.
    DEBUG is a flag to enable debug mode. Defaults to False.

    If the config file already exists, the command will exit with a non-zero exit code.


    Example:

    bisheng init --config-dir /path/to/config/ --engine_type gaab bisheng.yaml --debug

    :param config_dir:
    :param engine_type:
    :param debug:
    :param filename:
    :return:
    """
    try:
        Runner.init_plan(config_dir, engine_type=engine_type, filename=filename, debug=debug)
    except FileExistsError:
        exit(ExitCode.CONFIG_ALREADY_EXISTS.value)


@cli.command(help="Run a print job.")
@click.option(
    "--config-dir",
    type=str,
    required=True,
    help="The directory location of the config yaml file",
    callback=validate_directory,
)
@click.option(
    "--num-threads",
    type=int,
    required=False,
    help="Number of threads used to run tests concurrently. If the number of threads is not provided, the thread "
         "count will be set to one.",
)
@click.option(
    "--verbose",
    is_flag=True,
    type=bool,
    required=False,
    help="Print verbose logs.",
    default=False,
)
# @click.pass_context
def run(config_dir: str, num_threads: Optional[int], verbose: bool):
    try:
        runner = Runner.load(config_dir)
        # click.confirm("Do you want to continue?", abort=True)
        runner.run(num_threads=num_threads, verbose=verbose)
    except PrintFailureError:
        exit(1)


if __name__ == '__main__':
    cli()

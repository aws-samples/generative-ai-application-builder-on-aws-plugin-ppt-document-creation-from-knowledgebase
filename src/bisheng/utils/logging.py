import logging

logger = logging.getLogger(__name__)


def log_run_start(verbose: bool, num_threads: int):
    logger.info(f"Starting generation...")
    if verbose:
        logger.info(f"Number of threads: {num_threads}")


def log_run_end():
    pass

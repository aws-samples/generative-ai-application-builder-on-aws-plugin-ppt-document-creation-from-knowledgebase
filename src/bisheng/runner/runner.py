import concurrent.futures
import os
import logging
import threading
from datetime import time
from typing import Optional
import sys
import yaml
from rich.progress import Progress

from pydantic import BaseModel

from bisheng.decoders.decoder_factory import DecoderFactory
from bisheng.utils.defaults import CONFIG_FILE_NAME
from bisheng.encoders.encoder_factory import EncoderFactory
from bisheng.engines import EngineFactory
from bisheng.engines.websocket_engine import WebSocketEngine
from bisheng.utils import log_run_start, defaults
from bisheng.utils.logging import log_run_end
from bisheng.utils.summary import create_markdown_summary


sys.path.append(".")
logger = logging.getLogger(__name__)


class Runner(BaseModel):

    config: dict

    @classmethod
    def load(cls, config_dir: Optional[str] = None, config_file: Optional[str] = CONFIG_FILE_NAME):
        """Loads a YAML CONFIG_FILE from the CONFIG_DIR directory.

        CONFIG_DIR is the name of the directory where the config file is stored.
        CONFIG_FILE is the name of the config file to load. Defaults to bisheng.yaml.

        :param cls:
        :param config_dir:
        :param config_file:
        :return:
        """
        config_path = os.path.join(config_dir or os.getcwd(), config_file)
        config = cls._load_yaml(config_path)
        return cls(config=config)

    @staticmethod
    def _generate_template_bedrock_config() -> dict:
        """
        Generates a template bedrock config.

        :return:
        """
        return {
            "engine": {
                "type": "bedrock",
                "aws_profile": "${AWS_PROFILE}",
                "aws_region": "${AWS_REGION}",
                "endpoint_url": "https://bedrock.${AWS_REGION}.amazonaws.com",
                "max_retry": 10,
                "retry_mode": "adaptive",
                "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
                "version": "bedrock-2023-05-31",
                "trace": "ENABLED",
                "guardrail_id": "None",
                "guardrail_version": "None",
                "hyperparameters": {
                    "max_tokens": 30000,
                    "temperature": 0,
                    "top_p": 1,
                    "top_k": 250,
                    "role": "user"
                }
            },
            "encoders": [{
                "type": "transparency-report",
                "report_dir": "<PATH_TO_OUTPUT>"
            }, {
                "type": "pptx",
                "path": "<PATH_TO_OUTPUT>",
                "append": False
            }],
            "decoder": {
                "type": "one-shot-pptx-with-context",
                "prompts_path": "<PATH_TO_INPUT>",
                "shots_path": "<PATH_TO_INPUT>",
                "context_path": "<PATH_TO_INPUT>",
                "instruction": {
                    "type": "one-shot-with-context"
                }
            }
        }

    @staticmethod
    def _generate_template_gaab_config() -> dict:
        """
        Generates a template gaab config.

        :return:
        """
        return {
            "engine": {
                "type": "gaab",
                "ws_url": "${WSS_URL}",
                "app_client_id": "${APP_CLIENT_ID}",
                "user_name": "${USER_NAME}",
                "password": "${PASSWORD}",
                "aws_profile": "${AWS_PROFILE}",
                "aws_region": "${AWS_REGION}",
                "endpoint_url": "https://bedrock.${AWS_REGION}.amazonaws.com",
                "max_retry": 10,
                "retry_mode": "adaptive",
            },
            "encoders": [{
                "type": "transparency-report",
                "report_dir": "<PATH_TO_OUTPUT>"
            }, {
                "type": "pptx",
                "path": "<PATH_TO_OUTPUT>",
                "append": False
            }],
            "decoder": {
                "type": "one-shot-pptx-with-context",
                "prompts_path": "<PATH_TO_INPUT>",
                "shots_path": "<PATH_TO_INPUT>",
                "context_path": "<PATH_TO_INPUT>",
                "instruction": {
                    "type": "one-shot-with-context"
                }
            }
        }

    @staticmethod
    def generate_initial_config(engine_type: str) -> dict:
        """
        Generates an initial config based on the engine type.

        :param engine_type:
        :return:
        """
        if engine_type == "gaab":
            return Runner._generate_template_gaab_config()
        elif engine_type == "bedrock":
            return Runner._generate_template_bedrock_config()
        else:
            raise ValueError(f"Invalid engine type: {engine_type}")

    @staticmethod
    def _resolve_num_threads(num_tests: int, num_threads: Optional[int]) -> int:
        """
        Resolves the number of threads to use for the test run.

        The number of threads is capped by the maximum number of threads allowed by the engine.
        If the number of threads is not specified, this resolves to the minimum of the number of tests and the maximum
        number of threads allowed by the engine.

        :param num_tests:
        :param num_threads:
        :return:
        """
        return (
            min(num_tests, defaults.MAX_NUM_THREADS)
            if num_threads is None
            else num_threads
        )

    @staticmethod
    def _load_yaml(path: str) -> dict:
        """
        Loads a YAML file from the given path.

        :param path:
        :return:
        """
        with open(path) as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def init_plan(
            config_dir: Optional[str] = None,
            engine_type: Optional[str] = "bedrock",
            debug: Optional[bool] = False,
            filename: Optional[str] = CONFIG_FILE_NAME,
    ) -> str:
        """
        Creates a default config file in the given directory.

        The config file is created with the given engine type. If the file already exists, an error is raised.

        :param config_dir:
        :param engine_type:
        :param debug:
        :param filename:
        :return:
        """
        logger.setLevel(logging.DEBUG) if debug else logger.setLevel(logging.INFO)

        config_path = os.path.join(config_dir or os.getcwd(), filename)
        logger.debug(f"Set configuration path to {config_path}")

        if os.path.exists(config_path):
            logger.error(f"Config already exists at {config_dir}")
            raise FileExistsError
        else:
            os.makedirs(config_dir)

        config_path = os.path.join(config_dir or os.getcwd(), filename)
        logger.debug(f"Set configuration path to {config_path}")

        if os.path.exists(config_path):
            logger.error(f"Config already exists at {config_dir}")
            raise FileExistsError

        with open(config_path, "w") as stream:
            logger.debug(f"Writing default config with engine type {engine_type}...")
            yaml.safe_dump(Runner.generate_initial_config(engine_type), stream, sort_keys=False)
        os.makedirs(os.path.join(config_dir or os.getcwd(), "reports"))

        logger.info(f"Config created at {config_path}")
        return config_path

    def _pre_run(self):
        self._encoders = []

        self._engine_factory = EngineFactory(config=self.config["engine"])

        self._encoder_factory = EncoderFactory(config=self.config["encoders"])
        for encoder in self.config["encoders"]:
            self._encoders.append(self._encoder_factory.create(encoder))

        self._decoder_factory = DecoderFactory(config=self.config["decoder"])
        self._decoder = self._decoder_factory.create()

        self._lock = threading.Lock()

    def _run_decoder(self, num_threads):
        self._decoder.decode()
        self._num_threads = self._resolve_num_threads(self._decoder.num_prompts, num_threads)
        self._results = {prompt: None for prompt in self._decoder.prompts}

    def run(self,
            num_threads: int = 1,
            verbose: bool = False,
            ):
        self._pre_run()
        self._run_decoder(num_threads)

        log_run_start(verbose, len(self._decoder.prompts))

        start = time()

        with Progress(transient=True) as self._progress:
            self._tracker = self._progress.add_task("running...", total=self._decoder.num_prompts)
            self._run_concurrent()

        if len(self._results) > 0:
            encoder_data = {
                        "results": self._results,
                        **self._decoder.get_encoder_metadata()
                    }

            for encoder in self._encoders:
                encoder.encode(**encoder_data)

        log_run_end(
            # verbose,
            # self._results,
            # self._num_tests,
            # self._pass_count,
            # fail_count,
            # round(time.time() - start, 2),
            # sum(self._evaluator_input_token_counts),
            # sum(self._evaluator_output_token_counts),
        )

        create_markdown_summary()

    def _run_concurrent(self):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._num_threads
        ) as executor:
            futures = [
                executor.submit(self._run_test, prompt) for prompt in self._decoder.prompts
            ]
            for future in concurrent.futures.as_completed(futures):
                future.result()

    def _run_test(self, prompt):
        engine = self._engine_factory.create()
        if isinstance(engine, WebSocketEngine):
            engine.connect()
            engine.wait_for_connection(timeout=2)
        results = engine.invoke(prompt)

        with self._lock:

            # if result.passed is True:
            #     self._pass_count += 1
            # self._results[prompt.name] = result
            # self._evaluator_input_token_counts.append(evaluator.input_token_count)
            # self._evaluator_output_token_counts.append(evaluator.output_token_count)
            self._results[prompt] = results
            self._progress.update(self._tracker, advance=1)


# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import re
import json
import uuid
from typing import Optional

from bisheng.engines.bedrock.response import BedrockResponse
from bisheng.engines.boto3_engine import Boto3Engine
from bisheng.prompting.base_prompt import BasePrompt

_SERVICE_NAME = 'bedrock-runtime'


class BedrockEngine(Boto3Engine):
    """A target encapsulating an Amazon Bedrock agent."""

    def __init__(self,
                 # model: dict,
                 model_id: str,
                 version: str,
                 trace: Optional[str],
                 guardrail_id: Optional[str],
                 guardrail_version: Optional[str],
                 hyperparameters: Optional[dict],
                 **kwargs):
        super().__init__(boto3_service_name=_SERVICE_NAME, **kwargs)
        # self._provider = model["provider"]
        # self._name = model["name"]
        self._model_id = model_id
        self._version = version
        self._trace = trace
        self._guardrail_id = guardrail_id
        self._guardrail_version = guardrail_version
        self._hyperparameters = hyperparameters
        self._session_id: str = str(uuid.uuid4())

    def invoke(self, prompt: BasePrompt):
        request_body = {"anthropic_version": self._version, "max_tokens": self._hyperparameters["max_tokens"],
                        "system": prompt.get_system_prompt(), "messages": [{
                            "role": self._hyperparameters["role"],
                            "content": [{"type": "text", "text": prompt.get_instruction_prompt()}, ],
                        }], "temperature": self._hyperparameters["temperature"],
                        "top_p": self._hyperparameters["top_p"],
                        "top_k": self._hyperparameters["top_k"]
                        }

        response = self.boto3_client.invoke_model(
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json',
            modelId=self._model_id,
            trace=self._trace
        ).get("body").read()

        response_text = json.loads(response)["content"][0]["text"]

        rationale_regex = r"<rationale>(.*)</rationale>"
        response_regex = r"<response>(.*)</response>"
        rationale_matches = re.findall(rationale_regex, response_text, re.DOTALL)
        response_matches = re.findall(response_regex, response_text, re.DOTALL)

        return BedrockResponse(
            rationale=rationale_matches[0] if len(rationale_matches) > 0 else "",
            response=response_matches[0] if len(response_matches) > 0 else "",
            sources=""
        )

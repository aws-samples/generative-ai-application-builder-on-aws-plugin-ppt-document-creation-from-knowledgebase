# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod
from typing import Optional

from bisheng.engines import BaseEngine
from bisheng.utils import create_boto3_client, generate_cognito_jwt_token


class WebSocketEngine(BaseEngine, ABC):

    def __init__(
        self,
        app_client_id: str,
        user_name: str,
        password: str,
        aws_profile: Optional[str],
        aws_region: Optional[str],
        endpoint_url: Optional[str],
        max_retry: int = 10,
        retry_mode: str = "adaptive"
    ):
        boto3_client = create_boto3_client(
            boto3_service_name="cognito-idp",
            aws_profile=aws_profile,
            aws_region=aws_region,
            endpoint_url=endpoint_url,
            max_retry=max_retry,
            retry_mode=retry_mode
        )
        self.token = generate_cognito_jwt_token(boto3_client, app_client_id, user_name, password)

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def wait_for_connection(self, timeout):
        pass

    @abstractmethod
    def on_open(self, ws):
        pass

    @abstractmethod
    def on_error(self, ws, error):
        print("WebSocket error:", error)

    @abstractmethod
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    @abstractmethod
    def on_message(self, ws, message):
        pass
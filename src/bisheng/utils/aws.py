from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.config import Config


def create_boto3_client(
    boto3_service_name: str,
    aws_profile: str,
    aws_region: str,
    endpoint_url: str,
    max_retry: int,
    retry_mode: str,
) -> BaseClient:

    config = Config(retries={"max_attempts": max_retry, "mode": retry_mode})

    session = boto3.Session(profile_name=aws_profile, region_name=aws_region)
    return session.client(boto3_service_name, config=config)


def generate_cognito_jwt_token(
        client: BaseClient,
        app_client_id: str,
        user_name: str,
        password: str
) -> str:
    response = client.initiate_auth(
        ClientId=app_client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": user_name, "PASSWORD": password},
    )
    token = response["AuthenticationResult"]["AccessToken"]
    return token

from typing import NoReturn, Optional

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client
from trafalgar_log.core.logger import Logger

from jwt_manager.app import SETTINGS
from jwt_manager.core.ports import TokenPort, CachePort
from jwt_manager.out.clients import TokenClient


class TokenAdapter(TokenPort):
    token_client = TokenClient(base_url=SETTINGS.get("URL"))

    # noinspection PyArgumentList
    def get_token(self) -> str:
        Logger.info("Token Adapter", "Generating new token.", "")
        return self.token_client.get_token()


class S3Adapter(CachePort):
    kwargs = {}
    aws_endpoint: str = SETTINGS.get("AWS_ENDPOINT")
    bucket_name: str = SETTINGS.get("S3_BUCKET")
    file_name: str = SETTINGS.get("CLIENT_ID")

    if aws_endpoint:
        kwargs["endpoint_url"] = aws_endpoint

    s3: S3Client = boto3.client("s3", **kwargs)

    def cache_exists(self) -> bool:
        try:
            Logger.info(
                "Token Adapter",
                f"Checking if file {self.file_name} "
                f"exists on bucket {self.bucket_name}.",
                "",
            )

            self.s3.head_object(Bucket=self.bucket_name, Key=self.file_name)
        except ClientError as e:
            Logger.error(
                "Token Adapter", f"File not found on bucket: {str(e)}", ""
            )

            return False
        except Exception as e:
            Logger.error(
                "Token Adapter",
                f"Error searching file on bucket: {str(e)}",
                "",
            )
            return False

        return True

    def get_cache_content(self) -> Optional[str]:
        try:
            Logger.info(
                "Token Adapter",
                f"Getting file {self.file_name} content "
                f"on bucket {self.bucket_name}."
                "",
            )
            return (
                self.s3.get_object(
                    Bucket=self.bucket_name,
                    Key=self.file_name,
                )
                .get("Body")
                .read()
            ).decode("utf-8")
        except ClientError as e:
            Logger.error(
                "Token Adapter",
                f"Error Getting file content on bucket: {str(e)}",
                "",
            )
            return None

    def update_cache(self, token: str) -> NoReturn:
        try:
            Logger.info(
                "Token Adapter",
                f"Creating/updating file {self.file_name} content "
                f"on bucket {self.bucket_name}.",
                "",
            )
            self.s3.put_object(
                Body=token,
                Bucket=self.bucket_name,
                Key=self.file_name,
            )
        except ClientError as e:
            Logger.error(
                "Token Adapter",
                f"Error creating/updating file content: {str(e)}",
                "",
            )

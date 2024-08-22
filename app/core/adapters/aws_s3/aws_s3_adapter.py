import boto3
from botocore.client import BaseClient

from app.dependencies import get_settings

settings = get_settings()

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)


async def get_s3_client() -> BaseClient:
    return s3_client

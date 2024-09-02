import uuid
from typing import Annotated

from boto3.exceptions import Boto3Error
from fastapi import Depends, UploadFile, HTTPException

from app.common.repositories.storage import StorageItemRepository
from app.core.adapters.aws_s3.aws_s3_adapter import s3_client


class StorageItemService:
    s3_client = s3_client

    def __init__(
            self,
            storage_item_repository: Annotated[
                StorageItemRepository, Depends()
            ]
    ) -> None:
        self.storage_item_repository = storage_item_repository

    @classmethod
    async def upload_file(
            cls,
            bucket_name: str,
            item_path: str,
            file: UploadFile
    ) -> str:
        file_extension = file.filename.split('.')[-1]
        unique_id = uuid.uuid4()
        stored_file_name = f'{unique_id}.{file_extension}'
        stored_file_path = f'{item_path}/{stored_file_name}'

        try:
            cls.s3_client.upload_fileobj(
                file.file,
                bucket_name,
                stored_file_path
            )
        except Boto3Error:
            raise HTTPException(
                status_code=500,
                detail='Error uploading file'
            )

        return stored_file_path

    @classmethod
    async def generate_presigned_url(
            cls,
            bucket_name: str,
            storage_path: str
    ) -> str:
        return cls.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': storage_path
            }
        )

    @classmethod
    async def delete_file(
            cls,
            bucket_name: str,
            storage_path: str
    ) -> bool:
        try:
            cls.s3_client.delete_object(
                Bucket=bucket_name,
                Key=storage_path
            )
        except Boto3Error:
            return False

        return True

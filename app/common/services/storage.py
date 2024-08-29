import uuid
from typing import Annotated

from boto3.exceptions import Boto3Error
from botocore.client import BaseClient
from fastapi import Depends, UploadFile, HTTPException

from app.common.repositories.storage import StorageItemRepository
from app.common.schemas import StorageItemCreateSchema
from app.core.adapters.aws_s3.aws_s3_adapter import get_s3_client


class StorageItemService:
    def __init__(
            self,
            storage_item_repository: Annotated[
                StorageItemRepository, Depends()
            ],
            s3_client: Annotated[BaseClient, Depends(get_s3_client)]
    ) -> None:
        self.s3_client = s3_client
        self.storage_item_repository = storage_item_repository

    async def upload_file(
            self,
            bucket_name: str,
            item_path: str,
            file: UploadFile
    ) -> int:
        file_extension = file.filename.split('.')[-1]
        unique_id = uuid.uuid4()
        stored_file_name = f'{unique_id}.{file_extension}'
        stored_file_path = f'{item_path}/{stored_file_name}'

        try:
            self.s3_client.upload_fileobj(
                file.file,
                bucket_name,
                stored_file_path
            )
        except Boto3Error:
            raise HTTPException(
                status_code=500,
                detail='Error uploading file'
            )

        item_model = await self.storage_item_repository.create(
            StorageItemCreateSchema(
                original_file_name=file.filename,
                stored_file_name=stored_file_name,
                storage_path=stored_file_path
            )
        )
        return item_model.id

    async def generate_presigned_url(
            self,
            bucket_name: str,
            item_id: int
    ) -> str | None:
        item_model = await self.storage_item_repository.get_by_id(item_id)
        if not item_model:
            return None

        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': item_model.storage_path
            }
        )

    async def delete_file(
            self,
            bucket_name: str,
            item_id: int
    ) -> bool:
        item_model = await self.storage_item_repository.get_by_id(item_id)
        if not item_model:
            return False

        self.s3_client.delete_object(
            Bucket=bucket_name,
            Key=item_model.storage_path
        )

        return True



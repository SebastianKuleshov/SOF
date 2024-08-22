from typing import Annotated

from boto3.exceptions import Boto3Error
from botocore.client import BaseClient
from fastapi import Depends, UploadFile, HTTPException

from app.core.adapters.aws_s3.aws_s3_adapter import get_s3_client
from app.dependencies import get_settings
from app.users.models import UserModel

settings = get_settings()


class S3Service:
    def __init__(
            self,
            s3_client: Annotated[BaseClient, Depends(get_s3_client)]
    ):
        self.s3_client = s3_client
        self.bucket_name = settings.AWS_BUCKET_NAME

    async def upload_file(
            self,
            user: UserModel,
            file: UploadFile
    ) -> str:
        object_name = f'avatars/{user.id}/{file.filename}'
        if file.content_type.split('/')[1] not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail='File type not allowed'
            )

        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_name
            )
        except Boto3Error:
            raise HTTPException(
                status_code=500,
                detail='Error uploading file'
            )

        if user.avatar_key.split('/')[2] != file.filename:
            await self.delete_file(user)
        return object_name

    async def delete_file(
            self,
            user: UserModel
    ) -> None:
        object_name = user.avatar_key
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
        except Boto3Error:
            raise HTTPException(
                status_code=500,
                detail='Error deleting file'
            )

    async def generate_presigned_url(
            self,
            avatar_key: str
    ) -> str | None:
        if avatar_key is None:
            return None
        object_name = avatar_key
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': object_name
            }
        )

from typing import Annotated

from boto3.exceptions import Boto3Error
from botocore.client import BaseClient
from fastapi import Depends, UploadFile, HTTPException

from app.aws_s3.models import S3FileModel
from app.aws_s3.schemas import S3FileBaseSchema
from app.aws_s3.services.repositories.aws_s3 import S3Repository
from app.core.adapters.aws_s3.aws_s3_adapter import get_s3_client
from app.dependencies import get_settings
from app.users.models import UserModel

settings = get_settings()


class S3Service:
    def __init__(
            self,
            s3_repository: Annotated[S3Repository, Depends()],
            s3_client: Annotated[BaseClient, Depends(get_s3_client)]
    ):
        self.s3_repository = s3_repository
        self.s3_client = s3_client
        self.bucket_name = settings.AWS_BUCKET_NAME

    async def get_avatar_key(
            self,
            user_id: int
    ) -> str | None:
        s3_file = await self.s3_repository.get_by_user_id_and_folder_name(
            user_id,
            'avatars'
        )
        return f'{s3_file.folder}/{s3_file.user_id}/{s3_file.name}' if s3_file else None

    async def upload_user_avatar(
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

        s3_file = await self.s3_repository.get_by_user_id_and_folder_name(
            user.id,
            'avatars'
        )

        if s3_file:
            await self.s3_repository.delete_by_user_id_and_folder_name(
                user.id,
                'avatars'
            )

        await self.s3_repository.create(
            S3FileBaseSchema(
                folder='avatars',
                name=file.filename,
                user_id=user.id
            )
        )

        if s3_file.name != file.filename:
            await self.delete_file(s3_file)
        return object_name

    async def delete_file(
            self,
            s3_file: S3FileModel
    ) -> None:
        object_name = f'{s3_file.folder}/{s3_file.user_id}/{s3_file.name}'
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
        await self.s3_repository.delete(s3_file.id)

    async def generate_avatar_presigned_url(
            self,
            user_id: int
    ) -> str | None:
        s3_file = await self.s3_repository.get_by_user_id_and_folder_name(
            user_id,
            'avatars'
        )
        if not s3_file:
            return None
        avatar_key = f'{s3_file.folder}/{s3_file.user_id}/{s3_file.name}'

        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': avatar_key
            }
        )

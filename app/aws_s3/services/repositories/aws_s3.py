from sqlalchemy import select, and_, delete

from app.aws_s3.models import S3FileModel
from app.common.repositories.base_repository import BaseRepository


class S3Repository(BaseRepository):
    model = S3FileModel

    async def get_by_user_id_and_folder_name(
            self,
            user_id: int,
            folder_name: str
    ) -> S3FileModel:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.folder == folder_name
            )
        )
        return await self.session.scalar(stmt)

    async def delete_by_user_id_and_folder_name(
            self,
            user_id: int,
            folder_name: str
    ) -> bool:
        stmt = delete(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.folder == folder_name
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True



from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.comments.models import CommentModel
from app.comments.schemas import CommentWithUserOutSchema
from app.common.repositories.base_repository import BaseRepository


class CommentRepository(BaseRepository):
    model = CommentModel

    async def check_comment_exists(self, comment_id: int) -> bool:
        comment = await self.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail='Comment not found'
            )
        return True

    async def get_by_id_with_user(
            self,
            comment_id: int
    ) -> CommentWithUserOutSchema:
        stmt = (select(self.model)
                .options(joinedload(self.model.user))
                .where(comment_id == self.model.id))
        comment = await self.session.scalar(stmt)
        return CommentWithUserOutSchema.model_validate(comment)

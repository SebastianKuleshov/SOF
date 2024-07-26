from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository):
    model = AnswerModel

    async def check_answer_exists(
            self,
            answer_id: int
    ) -> bool:
        stmt = select(self.model).where(answer_id == self.model.id)
        question = await self.session.scalar(stmt)
        if not question:
            raise HTTPException(
                status_code=404,
                detail='Question not found'
            )
        return True

    async def get_by_id_with_user(self, answer_id: int):
        stmt = (select(self.model)
                .options(joinedload(self.model.user))
                .where(answer_id == self.model.id))
        answer = await self.session.scalar(stmt)
        return answer

    async def get_by_id_with_joins(self, answer_id: int):
        stmt = (select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.question)
        ).where(answer_id == self.model.id))
        answer = await self.session.scalar(stmt)
        return answer

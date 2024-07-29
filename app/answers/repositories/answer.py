from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.answers.schemas import AnswerWithUserSchema, AnswerWithJoinsOutSchema, \
    AnswerOutSchema
from app.common.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository):
    model = AnswerModel

    async def get_answer_if_exists(
            self,
            answer_id: int
    ) -> AnswerOutSchema | None:
        answer = await self.get_by_id(answer_id)
        if not answer:
            raise HTTPException(
                status_code=404,
                detail='Answer not found'
            )
        return AnswerOutSchema.model_validate(answer)

    async def get_by_id_with_user(
            self,
            answer_id: int
    ) -> AnswerWithUserSchema:
        stmt = (select(self.model)
                .options(joinedload(self.model.user))
                .where(answer_id == self.model.id))
        answer = await self.session.scalar(stmt)
        return AnswerWithUserSchema.model_validate(answer)

    async def get_by_id_with_joins(
            self,
            answer_id: int
    ) -> AnswerWithJoinsOutSchema:
        stmt = (select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.question)
        ).where(answer_id == self.model.id))
        answer = await self.session.scalar(stmt)
        return AnswerWithJoinsOutSchema.model_validate(answer)

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.answers.schemas import AnswerWithUserOutSchema, \
    AnswerWithJoinsOutSchema
from app.common.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository):
    model = AnswerModel

    async def get_by_id_with_user(
            self,
            answer_id: int
    ) -> AnswerWithUserOutSchema:
        stmt = (select(self.model)
                .options(joinedload(self.model.user))
                .where(answer_id == self.model.id))
        answer = await self.session.scalar(stmt)
        return AnswerWithUserOutSchema.model_validate(answer)

    async def get_by_id_with_joins(
            self,
            answer_id: int
    ) -> AnswerWithJoinsOutSchema:
        stmt = (select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.question)
        ).where(answer_id == self.model.id))
        answer = await self.session.scalar(stmt)
        return AnswerWithJoinsOutSchema.model_validate(
            answer
        ) if answer else None

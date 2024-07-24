from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.common.repositories.base_repository import BaseRepository
from app.questions.schemas import QuestionWithUserOutSchema
from app.questions.models import QuestionModel


class QuestionRepository(BaseRepository):
    model = QuestionModel

    async def get_question_by_id(
            self,
            question_id: int
    ) -> QuestionWithUserOutSchema | None:
        stmt = (select(self.model)
                .options(joinedload(self.model.user))
                .where(question_id == self.model.id)
                )
        question = await self.session.scalar(stmt)
        return QuestionWithUserOutSchema.model_validate(
            question
        ) if question else None

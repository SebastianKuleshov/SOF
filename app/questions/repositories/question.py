from fastapi import HTTPException
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

    async def check_question_exists(
            self,
            question_id: int
    ) -> bool:
        stmt = select(self.model).where(question_id == self.model.id)
        question = await self.session.scalar(stmt)
        if not question:
            raise HTTPException(
                status_code=404,
                detail='Question not found'
            )
        return True

    async def get_user_questions(
            self,
            user_id: int
    ) -> list[QuestionWithUserOutSchema]:
        stmt = (select(self.model)
                .options(joinedload(self.model.user))
                .where(user_id == self.model.user_id)
                )
        questions = await self.session.scalars(stmt)
        questions = questions.unique().all()
        return [
            QuestionWithUserOutSchema.model_validate(question) for question in
            questions
        ]

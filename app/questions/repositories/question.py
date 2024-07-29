from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel
from app.questions.schemas import QuestionWithUserOutSchema, \
    QuestionWithJoinsOutSchema, QuestionForListOutSchema


class QuestionRepository(BaseRepository):
    model = QuestionModel

    async def check_question_exists(
            self,
            question_id: int
    ) -> bool:
        question = await self.get_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=404,
                detail='Question not found'
            )
        return True

    async def get_by_id_with_user(
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

    async def get_by_id_with_joins(
            self,
            question_id: int
    ) -> QuestionWithJoinsOutSchema | None:
        stmt = (select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.answers)
        ).where(question_id == self.model.id))
        question = await self.session.scalar(stmt)
        return question

    async def get_list_with_joins(
            self,
            offset: int,
            limit: int
    ) -> list[QuestionForListOutSchema]:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.user),
                joinedload(self.model.answers)
            )
            .offset(offset)
            .limit(limit)
            .order_by(self.model.created_at.asc())
        )
        questions = await self.session.scalars(stmt)
        questions = questions.unique().all()
        return [
            QuestionForListOutSchema.model_validate(
                {
                    **question.__dict__,
                    'answer_count': len(question.answers)
                }
            )
            for question in questions
        ]

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
            QuestionWithUserOutSchema.model_validate(question)
            for question in questions
        ]

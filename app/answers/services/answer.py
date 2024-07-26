from typing import Annotated

from fastapi import Depends

from app.answers.repositories import AnswerRepository
from app.answers.schemas import AnswerCreateSchema, AnswerUpdateSchema
from app.questions.repositories import QuestionRepository
from app.users.repositories import UserRepository


class AnswerService:
    def __init__(
            self,
            answer_repository: Annotated[AnswerRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.answer_repository = answer_repository
        self.question_repository = question_repository
        self.user_repository = user_repository

    async def create_answer(
            self,
            answer_schema: AnswerCreateSchema
    ):
        await self.user_repository.check_user_exists(
            answer_schema.user_id
        )
        await self.question_repository.check_question_exists(
            answer_schema.question_id
        )
        return await self.answer_repository.create(answer_schema)

    async def get_answer(
            self,
            answer_id: int
    ):
        await self.answer_repository.check_answer_exists(answer_id)
        return await self.answer_repository.get_by_id_with_joins(answer_id)

    async def update_answer(
            self,
            answer_id: int,
            answer_schema: AnswerUpdateSchema
    ):
        await self.answer_repository.check_answer_exists(answer_id)
        await self.answer_repository.update(answer_id, answer_schema)
        return await self.answer_repository.get_by_id_with_user(answer_id)

    async def delete_answer(
            self,
            answer_id: int
    ):
        await self.answer_repository.check_answer_exists(answer_id)
        return await self.answer_repository.delete(answer_id)

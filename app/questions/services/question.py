from typing import Annotated

from fastapi import Depends, HTTPException

from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema, QuestionCreateSchema, \
    QuestionWithUserOutSchema, QuestionOutSchema
from app.users.repositories import UserRepository


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.user_repository = user_repository

    async def create_question(
            self,
            question_schema: QuestionCreateSchema
    ) -> QuestionOutSchema:
        await self.user_repository.check_user_exists(question_schema.user_id)
        question_model = await self.question_repository.create(question_schema)
        return QuestionOutSchema.model_validate(question_model)

    async def get_question(
            self,
            question_id: int
    ) -> QuestionWithUserOutSchema:
        await self.question_repository.check_question_exists(question_id)
        return await self.question_repository.get_question_by_id(
            question_id
        )

    async def update_question(
            self,
            question_id: int,
            question_schema: QuestionUpdateSchema
    ) -> QuestionWithUserOutSchema:
        await self.question_repository.check_question_exists(question_id)
        await self.question_repository.update(question_id, question_schema)
        return await self.question_repository.get_question_by_id(question_id)

    async def delete_question(
            self,
            question_id: int
    ):
        await self.question_repository.check_question_exists(question_id)
        return await self.question_repository.delete(question_id)

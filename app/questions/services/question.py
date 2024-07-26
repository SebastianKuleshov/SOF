from typing import Annotated

from fastapi import Depends

from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema, QuestionCreateSchema, \
    QuestionWithUserOutSchema, QuestionOutSchema, QuestionWithJoinsOutSchema
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
    ) -> QuestionWithJoinsOutSchema:
        await self.question_repository.check_question_exists(question_id)
        return await self.question_repository.get_by_id_with_joins(
            question_id
        )

    async def get_questions(
            self,
            skip: int = 0,
            limit: int = 100
    ):
        return await self.question_repository.get_list_with_joins(skip, limit)

    async def get_user_questions(
            self,
            user_id: int
    ) -> list[QuestionWithUserOutSchema]:
        await self.user_repository.check_user_exists(user_id)
        return await self.question_repository.get_user_questions(user_id)

    async def update_question(
            self,
            question_id: int,
            question_schema: QuestionUpdateSchema
    ) -> QuestionOutSchema:
        await self.question_repository.check_question_exists(question_id)
        await self.question_repository.update(question_id, question_schema)
        return await self.question_repository.get_by_id_with_user(question_id)

    async def delete_question(
            self,
            question_id: int
    ):
        await self.question_repository.check_question_exists(question_id)
        return await self.question_repository.delete(question_id)

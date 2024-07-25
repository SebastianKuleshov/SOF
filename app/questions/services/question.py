from typing import Annotated

from fastapi import Depends, HTTPException

from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository

    async def get_question(
            self,
            question_id: int
    ):
        await self.question_repository.check_question_exists(question_id)
        return await self.question_repository.get_question_by_id(
            question_id
        )

    async def update_question(
            self,
            question_id: int,
            question_schema: QuestionUpdateSchema
    ):
        await self.question_repository.check_question_exists(question_id)
        await self.question_repository.update(question_id, question_schema)
        return await self.question_repository.get_question_by_id(question_id)

    async def delete_question(
            self,
            question_id: int
    ):
        await self.question_repository.check_question_exists(question_id)
        return await self.question_repository.delete(question_id)

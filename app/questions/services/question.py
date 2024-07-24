from typing import Annotated

from fastapi import Depends

from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository

    async def update(self, question_id: int, question: QuestionUpdateSchema):
        await self.question_repository.update(question_id, question)
        return await self.question_repository.get_question_by_id(question_id)

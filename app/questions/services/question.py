from typing import Annotated

from fastapi import Depends

from app.questions.repositories import QuestionRepository


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository

    pass

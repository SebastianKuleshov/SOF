from typing import Annotated

from fastapi import Depends

from app.answers.repositories import AnswerRepository


class AnswerService:
    def __init__(
            self,
            answer_repository: Annotated[AnswerRepository, Depends()]
    ) -> None:
        self.answer_repository = answer_repository

    pass

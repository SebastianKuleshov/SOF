from typing import Annotated

from fastapi import Depends

from app.questions.repositories import QuestionRepository
from app.tags.repositories import TagRepository
from app.users.repositories import UserRepository


class ReportService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            tag_repository: Annotated[TagRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.tag_repository = tag_repository
        self.question_repository = question_repository

    async def generate_report(self):
        return await self.user_repository.get_top_contributors()
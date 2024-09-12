from typing import Annotated

from fastapi import Depends
from sqlalchemy import Sequence

from app.auth.schemas import EmailCreatePayloadSchema
from app.common.services import EmailService
from app.common.utils import generate_csv
from app.core.adapters.postgres.postgres_adapter import Base
from app.dependencies import get_settings
from app.questions.models import QuestionModel
from app.questions.repositories import QuestionRepository
from app.tags.models import TagModel
from app.tags.repositories import TagRepository
from app.users.models import UserModel
from app.users.repositories import UserRepository


class ReportService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            tag_repository: Annotated[TagRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            email_service: Annotated[EmailService, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.tag_repository = tag_repository
        self.question_repository = question_repository
        self.email_service = email_service

    async def __get_reporting_data(
            self
    ) -> dict[str, Sequence[Base]]:
        top_contributors = await self.user_repository.get_top_contributors()
        top_tags = await self.tag_repository.get_top_tags()
        questions_without_answer = await self.question_repository.get_questions_without_answer()
        questions_without_accepted_answer = await self.question_repository.get_questions_without_accepted_answer()
        return {
            'top_contributors': top_contributors,
            'top_tags': top_tags,
            'questions_without_answer': questions_without_answer,
            'questions_without_accepted_answer': questions_without_accepted_answer
        }

    @staticmethod
    async def __generate_top_contributors_section(
            top_contributors: Sequence[UserModel]
    ) -> tuple[str, list[str], list[list[any]]]:
        return (
            'Top Contributors',
            [
                'User ID',
                'User nickname',
                'Total answers',
                'Answers amount within the last 24 hours',
                'Average answers amount per week',
                'Total answer upvotes',
                'Average upvotes per answer received',
                'Total answer downvotes',
                'Average downvotes per answer received'
            ],
            [
                [
                    user[0], user[1], user[2], user[3], user[4],
                    user[5], user[6], user[7], user[8]
                ]
                for user in top_contributors
            ]
        )

    @staticmethod
    async def __generate_top_tags_section(
            top_tags: Sequence[TagModel]
    ) -> tuple[str, list[str], list[list[any]]]:
        return (
            'Top Tags',
            [
                'Tag name',
                'Total tag usage count',
                'Last 12 hours tag usage count',
                'Last 1.5 hours tag usage count'
            ],
            [
                [
                    tag[0], tag[1], tag[2], tag[3]
                ]
                for tag in top_tags
            ]
        )

    @staticmethod
    async def __generate_questions_section(
            section_name: str,
            questions: Sequence[QuestionModel]
    ) -> tuple[str, list[str], list[list[any]]]:
        return (
            section_name,
            [
                'Question ID',
                'Question title',
            ],
            [
                [
                    question.id, question.title
                ]
                for question in questions
            ]
        )

    async def __generate_csv(
            self,
            reporting_data: dict[
                str,
                Sequence[Base]
            ]
    ) -> str:
        sections = [
            await self.__generate_top_contributors_section(
                reporting_data['top_contributors']
            ),
            await self.__generate_top_tags_section(reporting_data['top_tags']),
            await self.__generate_questions_section(
                'Questions without answer',
                reporting_data['questions_without_answer']
            ),
            await self.__generate_questions_section(
                'Questions without accepted answer',
                reporting_data['questions_without_accepted_answer']
            )
        ]
        return await generate_csv(sections)

    async def __send_report(
            self,
            csv_value: str
    ) -> bool:
        settings = get_settings()

        return await self.email_service.send_email(
            EmailCreatePayloadSchema(
                recipient=settings.SUPERUSER_EMAIL,
                subject='Statistics report',
                body='Report attached',
                attachments=[{
                    'content': csv_value,
                    'filename': 'report.csv'
                }]
            )
        )

    async def generate_and_send_report(
            self
    ) -> bool:
        reporting_data = await self.__get_reporting_data()
        csv_value = await self.__generate_csv(reporting_data)
        return await self.__send_report(csv_value)

from typing import Annotated

from fastapi import Depends

from app.auth.schemas import EmailCreatePayloadSchema
from app.common.services import EmailService
from app.common.utils import generate_csv
from app.dependencies import get_settings
from app.questions.repositories import QuestionRepository
from app.tags.repositories import TagRepository
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

    async def generate_and_send_report(self):
        top_contributors = await self.user_repository.get_top_contributors()
        top_tags = await self.tag_repository.get_top_tags()
        questions_with_no_answer = await self.question_repository.get_questions_with_no_answer()
        questions_with_no_accepted_answer = await self.question_repository.get_questions_with_no_accepted_answer()

        sections = [
            (
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
            ),
            (
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
            ),
            (
                'Questions with no answer',
                [
                    'Question ID',
                    'Question title',
                ],
                [
                    [
                        question.id, question.title
                    ]
                    for question in questions_with_no_answer
                ]
            ),
            (
                'Questions with no accepted answer',
                [
                    'Question ID',
                    'Question title',
                ],
                [
                    [
                        question.id, question.title
                    ]
                    for question in questions_with_no_accepted_answer
                ]
            )
        ]

        csv_value = await generate_csv(sections)

        settings = get_settings()

        await self.email_service.send_email(
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

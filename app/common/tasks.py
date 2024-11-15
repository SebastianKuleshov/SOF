import asyncio

from app.common.services import ReportService, EmailService
from app.core.adapters.celery.celery_adapter import celery_app
from app.core.adapters.postgres.postgres_adapter import async_session
from app.questions.repositories import QuestionRepository
from app.tags.repositories import TagRepository
from app.users.repositories import UserRepository


async def generate_and_send_report() -> None:
    async with async_session() as session:
        user_repository = UserRepository(session)
        tag_repository = TagRepository(session)
        question_repository = QuestionRepository(session)
        email_service = EmailService()
        report_service = ReportService(
            user_repository,
            tag_repository,
            question_repository,
            email_service
        )
        await report_service.generate_and_send_report()


@celery_app.task()
def generate_and_send_report_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_and_send_report())

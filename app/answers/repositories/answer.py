from app.common.repositories.base_repository import BaseRepository
from app.answers.models import Answer


class AnswerRepository(BaseRepository):
    model = Answer

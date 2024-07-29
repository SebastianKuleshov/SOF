from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository):
    model = AnswerModel

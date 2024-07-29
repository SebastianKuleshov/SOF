from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel


class QuestionRepository(BaseRepository):
    model = QuestionModel

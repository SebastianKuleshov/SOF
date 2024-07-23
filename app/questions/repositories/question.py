from app.common.repositories.base_repository import BaseRepository
from app.questions.models import Question


class QuestionRepository(BaseRepository):
    model = Question

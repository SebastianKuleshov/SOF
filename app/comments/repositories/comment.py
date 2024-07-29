from app.comments.models import CommentModel
from app.common.repositories.base_repository import BaseRepository


class CommentRepository(BaseRepository):
    model = CommentModel

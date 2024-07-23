from app.common.repositories.base_repository import BaseRepository
from app.comments.models import Comment


class CommentRepository(BaseRepository):
    model = Comment

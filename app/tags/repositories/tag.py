from app.common.repositories.base_repository import BaseRepository
from app.tags.models import TagModel


class TagRepository(BaseRepository):
    model = TagModel

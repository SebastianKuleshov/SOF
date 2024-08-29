from app.common.models import StorageItemModel
from app.common.repositories.base_repository import BaseRepository


class StorageItemRepository(BaseRepository):
    model = StorageItemModel

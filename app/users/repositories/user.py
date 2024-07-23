from app.common.repositories.base_repository import BaseRepository
from app.users.models import User


class UserRepository(BaseRepository):
    model = User

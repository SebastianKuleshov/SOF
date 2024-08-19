from app.common.repositories.base_repository import BaseRepository
from app.roles.models import RoleModel


class RoleRepository(BaseRepository):
    model = RoleModel

from sqlalchemy import select, ScalarResult

from app.common.repositories.base_repository import BaseRepository
from app.roles.models import RoleModel


class RoleRepository(BaseRepository):
    model = RoleModel

    async def get_roles_by_name(
            self,
            role_names: list[str]
    ) -> list[RoleModel]:
        stmt = select(self.model).where(
            self.model.name.in_(role_names)
        )
        roles = await self.session.scalars(stmt)
        return list(roles)

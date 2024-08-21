from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.common.repositories.base_repository import BaseRepository
from app.permissions.models import PermissionModel
from app.roles.models import RoleModel


class PermissionRepository(BaseRepository):
    model = PermissionModel

    def _get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.roles)
        )

    async def attach_permission_to_role(
            self,
            permission: PermissionModel,
            role: RoleModel
    ) -> bool:
        role.permissions.append(permission)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='Permission is already attached to the role'
            )
        return True

    # TODO CHECK ATTACH TAGS TO QUESTIONS

    async def detach_permission_from_role(
            self,
            permission: PermissionModel,
            role: RoleModel
    ) -> bool:
        permission.roles.remove(role)
        await self.session.commit()
        return True

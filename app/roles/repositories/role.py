from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.common.repositories.base_repository import BaseRepository
from app.roles.models import RoleModel
from app.users.models import UserModel


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

    async def attach_role_to_user(
            self,
            role: RoleModel,
            user: UserModel
    ) -> bool:
        user.roles.append(role)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='Role is already attached to the user'
            )
        return True

    async def detach_role_from_user(
            self,
            role: RoleModel,
            user: UserModel
    ) -> bool:
        user.roles.remove(role)
        await self.session.commit()
        return True

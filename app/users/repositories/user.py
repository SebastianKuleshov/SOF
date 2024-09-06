from fastapi import HTTPException
from sqlalchemy import select, Select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.common.repositories.base_repository import BaseRepository
from app.roles.models import RoleModel
from app.users.models import UserModel


class UserRepository(BaseRepository):
    model = UserModel

    def _get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.roles).joinedload(RoleModel.permissions)
        )

    async def update_reputation(
            self,
            user_id: int,
            is_upvote: bool
    ) -> int:
        user = await self.get_by_id(user_id)
        user.reputation += 1 if is_upvote else -1
        await self.session.commit()
        return user.reputation

    async def get_by_id_with_roles(
            self,
            user_id: int
    ) -> UserModel:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.roles)
                .joinedload(RoleModel.permissions),
            )
            .where(user_id == self.model.id)
        )
        return await self.session.scalar(stmt)

    async def get_user_permissions(
            self,
            user_id: int
    ) -> set[str]:
        stmt = text(
            '''SELECT permissions_1.name
            FROM users LEFT OUTER JOIN (role_user AS role_user_1 JOIN permission_role AS permission_role_1 ON role_user_1.role_id = permission_role_1.role_id JOIN permissions AS permissions_1 ON permissions_1.id = permission_role_1.permission_id) ON users.id = role_user_1.user_id
            WHERE users.id = :user_id;
            '''
        )
        result = await self.session.scalars(stmt, {'user_id': user_id})
        return set(result.all())

    async def attach_roles_to_user(
            self,
            user_id: int,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.get_by_id_with_roles(user_id)
        for role in roles:
            user.roles.append(role)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='Role is already attached to the user'
            )
        return True

    async def detach_roles_from_user(
            self,
            user_id: int,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.get_by_id_with_roles(user_id)
        try:
            for role in roles:
                user.roles.remove(role)
            await self.session.commit()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail='Role is not attached to the user'
            )
        return True

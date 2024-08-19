from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.common.repositories.base_repository import BaseRepository
from app.roles.models import RoleModel
from app.users.models import UserModel


class UserRepository(BaseRepository):
    model = UserModel

    async def update_reputation(
            self,
            user_id: int,
            is_upvote: bool
    ) -> None:
        user = await self.get_by_id(user_id)
        user.reputation += 1 if is_upvote else -1
        await self.session.commit()

    async def get_by_id_with_roles(
            self,
            user_id: int
    ) -> UserModel:
        stmt = (
            select(self.model).
            options(joinedload(self.model.roles))
            .where(user_id == self.model.id)
        )
        return await self.session.scalar(stmt)

    async def attach_roles_to_user(
            self,
            user_id: int,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.get_by_id_with_roles(user_id)
        user.roles = roles
        await self.session.commit()
        return True

    async def detach_roles_from_user(
            self,
            user_id: int,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.get_by_id_with_roles(user_id)
        user.roles = [role for role in user.roles if role not in roles]
        await self.session.commit()
        return True

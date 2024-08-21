from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.roles.repositories.role import RoleRepository
from app.roles.schemas import RoleBaseSchema, RoleOutSchema
from app.users.repositories import UserRepository


class RoleService:
    def __init__(
            self,
            role_repository: Annotated[RoleRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.role_repository = role_repository
        self.user_repository = user_repository

    async def create_role(
            self,
            role_schema: RoleBaseSchema
    ) -> RoleOutSchema:
        try:
            role_model = await self.role_repository.create(role_schema)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Role already exists"
            )
        return RoleOutSchema.model_validate(role_model)

    async def attach_role_to_user(
            self,
            role_id: int,
            user_id: int
    ) -> bool:
        role = await self.role_repository.get_entity_if_exists(role_id)
        user = await self.user_repository.get_entity_if_exists(user_id)
        if not role:
            raise HTTPException(
                status_code=404,
                detail="Role not found"
            )
        return await self.role_repository.attach_role_to_user(
            role,
            user
        )

    async def detach_role_from_user(
            self,
            role_id: int,
            user_id: int
    ):
        role = await self.role_repository.get_entity_if_exists(role_id)
        user = await self.user_repository.get_entity_if_exists(user_id)
        if role not in user.roles:
            raise HTTPException(
                status_code=400,
                detail="Role is not attached to the user"
            )

        return await self.role_repository.detach_role_from_user(
            role,
            user
        )

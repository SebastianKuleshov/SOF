from typing import Annotated

from asyncpg import UniqueViolationError
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError

from app.permissions.repositories import PermissionRepository
from app.permissions.schemas import PermissionBaseSchema, PermissionOutSchema
from app.roles.repositories import RoleRepository


class PermissionService:
    def __init__(
            self,
            permission_repository: Annotated[PermissionRepository, Depends()],
            role_repository: Annotated[RoleRepository, Depends()]
    ) -> None:
        self.permission_repository = permission_repository
        self.role_repository = role_repository

    async def create_permission(
            self,
            permission_schema: PermissionBaseSchema
    ) -> PermissionOutSchema:
        try:
            permission_model = await self.permission_repository.create(
                permission_schema
            )
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Permission already exists"
            )

        if permission_schema.attach_to_superuser:
            roles = await self.role_repository.get_roles_by_name(['superuser'])
            await self.permission_repository.attach_permission_to_role(
                permission_model,
                roles[0]
            )
        return PermissionOutSchema.model_validate(permission_model)

    async def attach_permission_to_role(
            self,
            permission_id: int,
            role_id: int
    ) -> bool:
        permission = await self.permission_repository.get_entity_if_exists(
            permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail="Permission not found"
            )

        role = await self.role_repository.get_entity_if_exists(role_id)

        return await self.permission_repository.attach_permission_to_role(
            permission,
            role
        )

    async def detach_permission_from_role(
            self,
            permission_id: int,
            role_id: int
    ) -> bool:
        await self.permission_repository.expire_session_for_all()
        permission = await self.permission_repository.get_by_id_with_joins(
            permission_id
        )
        if not permission:
            raise HTTPException(
                status_code=404,
                detail="Permission not found"
            )

        role = await self.role_repository.get_entity_if_exists(role_id)

        if role not in permission.roles:
            raise HTTPException(
                status_code=404,
                detail="Permission is not attached to the role"
            )

        return await self.permission_repository.detach_permission_from_role(
            permission,
            role
        )

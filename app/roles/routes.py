from typing import Annotated

from fastapi import APIRouter, Depends

from app.roles import schemas as role_schemas
from app.roles.services.role import RoleService

router = APIRouter(
    prefix='/roles',
    tags=['roles']
)


@router.get(
    '/',
    response_model=list[role_schemas.RoleOutSchema]
)
async def get_roles(
        role_service: Annotated[RoleService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await role_service.role_repository.get_multi(skip, limit)


@router.get(
    '/{role_id}',
    response_model=role_schemas.RoleOutSchema
)
async def get_role(
        role_service: Annotated[RoleService, Depends()],
        role_id: int
):
    return await role_service.role_repository.get_entity_if_exists(role_id)

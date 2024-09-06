from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.roles import schemas as role_schemas
from app.roles.services.role import RoleService

router = APIRouter(
    prefix='/roles',
    tags=['roles'],
    dependencies=[
        Depends(AuthService.get_user_from_jwt),
        Depends(AuthService.require_permissions({'create_role', 'attach_role'}))
    ]
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


@router.post(
    '/',
    response_model=role_schemas.RoleOutSchema
)
async def create_role(
        role_service: Annotated[RoleService, Depends()],
        role: role_schemas.RoleBaseSchema
):
    return await role_service.create_role(role)


@router.post(
    '/{role_id}/{user_id}',
)
async def attach_role_to_user(
        role_service: Annotated[RoleService, Depends()],
        role_id: int,
        user_id: int
) -> bool:
    return await role_service.attach_role_to_user(
        role_id,
        user_id
    )

@router.delete(
    '/{role_id}/{user_id}',
)
async def detach_role_from_user(
        role_service: Annotated[RoleService, Depends()],
        role_id: int,
        user_id: int
) -> bool:
    return await role_service.detach_role_from_user(
        role_id,
        user_id
    )

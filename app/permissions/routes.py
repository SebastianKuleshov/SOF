from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from app.auth.services import AuthService
from app.permissions import schemas as permission_schemas
from app.permissions.services import PermissionService

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"],
    dependencies=[
        Depends(AuthService.get_user_from_jwt),
        Depends(
            AuthService.PermissionChecker(
                ['create_permission', 'attach_permission']
            )
        )
    ]
)


@router.post(
    '/',
    response_model=permission_schemas.PermissionOutSchema
)
async def create_permission(
        permission_service: Annotated[PermissionService, Depends()],
        permission_schema: permission_schemas.PermissionBaseSchema
):
    return await permission_service.create_permission(
        permission_schema
    )


@router.get(
    '/',
    response_model=list[permission_schemas.PermissionOutSchema]
)
async def get_permissions(
        permission_service: Annotated[PermissionService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await permission_service.permission_repository.get_multi(
        skip,
        limit
    )


@router.post(
    '/{permission_id}/{role_id}',
)
async def attach_permission_to_role(
        permission_service: Annotated[PermissionService, Depends()],
        permission_id: int,
        role_id: int
) -> bool:
    return await (
        permission_service.attach_permission_to_role(
            permission_id,
            role_id
        )
    )


@router.delete(
    '/{permission_id}/{role_id}',
)
async def detach_permission_from_role(
        permission_service: Annotated[PermissionService, Depends()],
        permission_id: int,
        role_id: int
) -> bool:
    return await (
        permission_service.detach_permission_from_role(
            permission_id,
            role_id
        )
    )

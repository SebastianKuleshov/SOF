from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from pydantic import Json

from app.auth.services import AuthService
from app.users import schemas as user_schemas
from app.users.services import UserService

public_router = APIRouter(
    prefix='/users',
    tags=['users']
)

private_router = APIRouter(
    prefix='/users',
    tags=['users'],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)


# Public routes


@public_router.get(
    '/',
    response_model=list[user_schemas.UserOutSchema]
)
async def get_users(
        user_service: Annotated[UserService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await user_service.get_users(skip, limit)


@public_router.get(
    '/{user_id}',
    response_model=user_schemas.UserOutSchema
)
async def get_user(
        user_service: Annotated[UserService, Depends()],
        user_id: int
):
    return await user_service.get_user(user_id)


# Private routes

@private_router.get(
    '/me/',
    response_model=user_schemas.UserOutSchema
)
async def get_current_user(
        user_service: Annotated[UserService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()]
):
    return await user_service.get_user(user_id)


@private_router.put(
    '/{user_id}',
    response_model=user_schemas.UserOutSchema
)
async def update_user(
        user_service: Annotated[UserService, Depends()],
        requesting_user_id: Annotated[
            AuthService.get_user_id_from_request, Depends()
        ],
        user_schema: Json[user_schemas.UserUpdateSchema],
        user_id: int,
        avatar_file: UploadFile | str = None
):
    return await user_service.update_user(
        user_id,
        requesting_user_id,
        user_schema,
        avatar_file
    )


@private_router.delete(
    '/{user_id}'
)
async def delete_current_user(
        user_service: Annotated[UserService, Depends()],
        requesting_user_id: Annotated[
            AuthService.get_user_id_from_request, Depends()
        ],
        user_id: int
) -> bool:
    return await user_service.delete_user(
        user_id,
        requesting_user_id
    )


@private_router.post(
    '/ban/{user_id}',
    dependencies=[Depends(AuthService.require_permissions({'ban_user'}))]
)
async def ban_user(
        user_service: Annotated[UserService, Depends()],
        requesting_user_id: Annotated[
            AuthService.get_user_id_from_request, Depends()
        ],
        target_user_id: int
) -> bool:
    return await user_service.ban_user(
        requesting_user_id,
        target_user_id
    )


@private_router.post(
    '/unban/{user_id}',
    dependencies=[Depends(AuthService.require_permissions({'unban_user'}))]
)
async def unban_user(
        user_service: Annotated[UserService, Depends()],
        target_user_id: int
) -> bool:
    return await user_service.unban_user(
        target_user_id
    )

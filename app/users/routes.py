from typing import Annotated

from fastapi import APIRouter, Depends

from app.users import schemas as user_schemas
from app.users.services import UserService
from app.auth.services import AuthService

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post(
    '/',
    response_model=user_schemas.UserOutSchema
)
async def create_user(
        user_service: Annotated[UserService, Depends()],
        user: user_schemas.UserCreateSchema
):
    return await user_service.create_user(user)


@router.get(
    '/',
    response_model=list[user_schemas.UserOutSchema],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def get_users(
        user_service: Annotated[UserService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await user_service.user_repository.get_multi(skip, limit)


@router.get(
    '/{user_id}',
    response_model=user_schemas.UserOutSchema
)
async def get_user(
        user_service: Annotated[UserService, Depends()],
        user_id: int
):
    return await user_service.user_repository.get_by_id(user_id)


@router.get(
    '/me',
    response_model=user_schemas.UserOutSchema
)
async def get_current_user(
        user: Annotated[AuthService.get_user_from_jwt, Depends()]
):
    return user


@router.put(
    '/{user_id}',
    response_model=user_schemas.UserUpdateSchema,
    dependencies=[Depends(AuthService.get_user_from_jwt)],
)
async def update_user(
        user_service: Annotated[UserService, Depends()],
        user_id: int,
        user_schema: user_schemas.UserUpdateSchema
):
    return await user_service.update_user(
        user_id,
        user_schema
    )


@router.delete(
    '/{user_id}',
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def delete_current_user(
        user_service: Annotated[UserService, Depends()],
        user_id: int
) -> bool:
    return await user_service.user_repository.delete(user_id)

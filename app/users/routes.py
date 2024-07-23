from typing import Annotated

from fastapi import APIRouter, Depends

from app.users import schemas
from app.users.services import UserService
from app.auth.services import AuthService

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/', response_model=schemas.UserOutSchema)
async def create_user(
        user_service: Annotated[UserService, Depends()],
        user: schemas.UserCreateSchema
):
    return await user_service.create_user(user)


@router.get('/', response_model=list[schemas.UserOutSchema])
async def get_users(
        user_service: Annotated[UserService, Depends()],
        token: Annotated[AuthService.get_user_from_jwt, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await user_service.user_repository.get_multi(skip, limit)


@router.get('{user_id}', response_model=schemas.UserOutSchema)
async def get_user(
        user_service: Annotated[UserService, Depends()],
        user_id: int
):
    return await user_service.user_repository.get_by_id(user_id)


@router.get('/me', response_model=schemas.UserOutSchema)
async def get_me(
        user: Annotated[AuthService.get_user_from_jwt, Depends()]
):
    return user


@router.put('{user_id}', response_model=schemas.UserUpdateSchema)
async def update_user(
        user_service: Annotated[UserService, Depends()],
        user_id: int,
        user: schemas.UserUpdateSchema
):
    return await user_service.user_repository.update(user_id, user)

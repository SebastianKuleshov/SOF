from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_password_hash, verify_password
from app.users.models import UserModel
from app.users.repositories import UserRepository
from app.users.schemas import UserCreateSchema, UserOutSchema, UserUpdateSchema


class UserService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.user_repository = user_repository

    async def create_user(
            self,
            user: UserCreateSchema
    ) -> UserOutSchema:
        user.password = await get_password_hash(user.password)
        user_model = await self.user_repository.create(user)
        return UserOutSchema.model_validate(user_model)

    async def update_user(
            self,
            user_id: int,
            user_schema: UserUpdateSchema
    ) -> UserUpdateSchema:
        user_model = await self.user_repository.get_by_id(user_id)
        if not user_model:
            raise HTTPException(
                status_code=404,
                detail='User not found'
            )

        try:
            user_model = await self.user_repository.update(
                user_id,
                user_schema
            )
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='Email already exists'
            )

        return UserUpdateSchema.model_validate(user_model)

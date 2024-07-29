from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_password_hash
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
        if await self.user_repository.get_one(
                {'email': user.email}
        ) is not None:
            raise HTTPException(
                status_code=400,
                detail='Email already exists'
            )
        user.password = await get_password_hash(user.password)
        user_model = await self.user_repository.create(user)
        return UserOutSchema.model_validate(user_model)

    async def update_user(
            self,
            target_user_id: int,
            requesting_user_id: int,
            user_schema: UserUpdateSchema
    ) -> UserUpdateSchema:
        user = await self.user_repository.get_user_if_exists(target_user_id)
        if user.id != requesting_user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this user'
            )

        try:
            user_model = await self.user_repository.update(
                target_user_id,
                user_schema
            )
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='Email already exists'
            )

        return UserUpdateSchema.model_validate(user_model)

    async def delete_user(
            self,
            target_user_id: int,
            requesting_user_id: int
    ) -> bool:
        user = await self.user_repository.get_user_if_exists(target_user_id)
        if user.id != requesting_user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this user'
            )
        return await self.user_repository.delete(target_user_id)

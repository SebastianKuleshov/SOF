from typing import Annotated

from fastapi import Depends
from pydantic import EmailStr

from app.dependencies import get_password_hash, verify_password
from app.users.models import UserModel
from app.users.repositories import UserRepository
from app.users.schemas import UserCreateSchema, UserOutSchema


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

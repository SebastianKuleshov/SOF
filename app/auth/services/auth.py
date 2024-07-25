from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import TokenBaseSchema
from app.users.schemas import UserOutSchema
from app.users.repositories import UserRepository
from app.dependencies import get_settings, verify_token
from app.users.services import UserService


class AuthService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            user_service: Annotated[UserService, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.user_service = user_service

    @staticmethod
    async def create_token(
            to_encode: dict,
            expires_delta: timedelta
    ) -> str:
        expire = datetime.now(timezone.utc) + expires_delta

        settings = get_settings()

        secret_key = settings.SECRET_KEY
        algorithm = settings.ALGORITHM

        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode,
            secret_key,
            algorithm
        )
        return encoded_jwt

    @classmethod
    async def get_user_from_jwt(
            cls,
            user_repository: Annotated[UserRepository, Depends()],
            payload: Annotated[dict, Depends(verify_token)]
    ) -> UserOutSchema | None:
        user_id = payload.get('sub')
        user = await user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return user

    async def __generate_token(
            self,
            user_id: int,
            nick_name: str
    ) -> TokenBaseSchema:
        settings = get_settings()

        to_encode = {'sub': user_id, 'nick_name': nick_name}

        access_token_expire_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_expire_delta = timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        access_token = await self.create_token(
            to_encode,
            access_token_expire_delta
        )

        refresh_token = await self.create_token(
            to_encode,
            refresh_token_expire_delta
        )

        return TokenBaseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

    async def login(
            self,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenBaseSchema:
        user = await self.user_service.authenticate_user(
            form_data.username,
            form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=400,
                detail='Incorrect email or password'
            )

        return await self.__generate_token(user.id, user.nick_name)

    async def refresh(
            self,
            refresh_token: str
    ) -> TokenBaseSchema:
        payload = await verify_token(refresh_token)
        user_id = payload.get('sub')
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return await self.__generate_token(user.id, user.nick_name)

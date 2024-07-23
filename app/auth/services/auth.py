from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schemas import TokenBaseSchema
from app.users.repositories import UserRepository
from app.dependencies import get_settings, verify_token
from app.users.schemas import UserOutSchema


class AuthService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.user_repository = user_repository

    @staticmethod
    async def create_token(
            token_type: str,
            to_encode: dict,
            expires_delta: int,
            secret_key: str,
            algorithm: str
    ):
        if token_type == 'access':
            expires_delta = timedelta(minutes=expires_delta)
        else:
            expires_delta = timedelta(days=expires_delta)

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            if token_type == 'access':
                expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            else:
                expire = datetime.now(timezone.utc) + timedelta(days=15)

        to_encode.update({'token_type': token_type, 'exp': expire})
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

    async def login(
            self,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenBaseSchema:
        user = await self.user_repository.authenticate_user(
            form_data.username,
            form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=400,
                detail='Incorrect email or password'
            )

        settings = get_settings()
        to_encode = {'sub': user.id, 'nick_name': user.nick_name}
        access_token = await self.create_token(
            'access',
            to_encode,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            settings.SECRET_KEY,
            settings.ALGORITHM
        )

        refresh_token = await self.create_token(
            'refresh',
            to_encode,
            settings.REFRESH_TOKEN_EXPIRE_DAYS,
            settings.SECRET_KEY,
            settings.ALGORITHM
        )

        return TokenBaseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

    async def refresh(
            self,
            refresh_token: str
    ) -> TokenBaseSchema:
        payload = await verify_token(refresh_token)
        user_id = payload.get('sub')
        refresh_expires_delta = payload.get('exp')
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        settings = get_settings()

        to_encode = {'sub': user.id, 'nick_name': user.nick_name}

        access_token = await self.create_token(
            'access',
            to_encode,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            settings.SECRET_KEY,
            settings.ALGORITHM
        )

        if (datetime.fromtimestamp(
                refresh_expires_delta
        ) - datetime.now() < timedelta(
            days=settings.REFRESH_TOKEN_UPDATE_THRESHOLD_DAYS
        )):
            refresh_token = await self.create_token(
                'refresh',
                to_encode,
                settings.REFRESH_TOKEN_EXPIRE_DAYS,
                settings.SECRET_KEY,
                settings.ALGORITHM
            )

        return TokenBaseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

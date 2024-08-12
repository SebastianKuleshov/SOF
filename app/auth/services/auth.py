from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.auth.schemas import TokenBaseSchema
from app.users.models import UserModel
from app.users.schemas import UserOutSchema
from app.users.repositories import UserRepository
from app.dependencies import get_settings, oauth2_scheme, verify_password
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

    @staticmethod
    async def get_user_id_from_request(request: Request) -> int:
        if not hasattr(request.state, 'user_id'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return request.state.user_id

    @classmethod
    async def get_user_from_jwt(
            cls,
            request: Request,
            user_repository: Annotated[UserRepository, Depends()],
            is_refresh: bool = False,
            token: str = Depends(oauth2_scheme)
    ) -> UserOutSchema | None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        settings = get_settings()

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            if is_refresh and payload.get('token_type') != 'refresh':
                raise credentials_exception
            user_id = payload.get('sub')
            if user_id is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        user = await user_repository.get_by_id(user_id)
        if user is None:
            raise credentials_exception

        request.state.user_id = user_id
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
        access_to_encode = to_encode.copy()
        access_to_encode.update({'token_type': 'access'})
        refresh_token_expire_delta = timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        refresh_to_encode = to_encode.copy()
        refresh_to_encode.update({'token_type': 'refresh'})

        access_token = await self.create_token(
            access_to_encode,
            access_token_expire_delta
        )

        refresh_token = await self.create_token(
            refresh_to_encode,
            refresh_token_expire_delta
        )

        return TokenBaseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

    async def __authenticate_user(
            self,
            email: EmailStr,
            password: str
    ) -> UserModel | None:
        user = await self.user_repository.get_one({'email': email})
        if not user:
            return None
        if not await verify_password(password, user.password):
            return None
        return user

    async def login(
            self,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenBaseSchema:
        user = await self.__authenticate_user(
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
            request: Request,
            refresh_token: str
    ) -> TokenBaseSchema:
        user = await self.get_user_from_jwt(
            request,
            self.user_repository,
            True,
            refresh_token
        )

        return await self.__generate_token(user.id, user.nick_name)

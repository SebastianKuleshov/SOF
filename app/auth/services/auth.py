from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, \
    HTTPAuthorizationCredentials
from pydantic import EmailStr

from app.auth.repositories import AuthRepository
from app.auth.schemas import TokenBaseSchema, EmailCreateSchema, \
    EmailCreatePayloadSchema
from app.common.schemas_mixins import PasswordCreationMixin
from app.common.services import EmailService
from app.dependencies import get_settings, oauth2_scheme, verify_password, \
    get_password_hash, reset_password_token_scheme
from app.users.models import UserModel
from app.users.repositories import UserRepository
from app.users.schemas import UserOutSchema
from app.users.services import UserService


class AuthService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            auth_repository: Annotated[AuthRepository, Depends()],
            user_service: Annotated[UserService, Depends()],
            email_service: Annotated[EmailService, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.auth_repository = auth_repository
        self.user_service = user_service
        self.email_service = email_service

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
            auth_repository: Annotated[AuthRepository, Depends()],
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
            token_exists = await auth_repository.check_token(user_id, token)
            if not token_exists:
                await auth_repository.delete_user_tokens(user_id)
                raise HTTPException(
                    status_code=400,
                    detail='Token is invalid'
                )

            if user_id is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        user = await user_repository.get_by_id(user_id)
        if user is None:
            raise credentials_exception

        request.state.user_id = user_id
        return user

    @classmethod
    async def get_user_id_from_reset_password_jwt(
            cls,
            user_repository: Annotated[UserRepository, Depends()],
            credentials: Annotated[HTTPAuthorizationCredentials, Depends(
                reset_password_token_scheme)]
    ) -> int:
        token = credentials.credentials
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

            user = await user_repository.get_one(
                {'email': payload.get('sub')}
            )
            if user is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        return user.id

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

        await self.auth_repository.create_tokens(
            user_id,
            refresh_token,
            access_token
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
            self.auth_repository,
            True,
            refresh_token
        )

        await self.auth_repository.delete_user_tokens(user.id)

        return await self.__generate_token(user.id, user.nick_name)

    async def forgot_password(
            self,
            email_schema: EmailCreateSchema
    ) -> bool:
        user = await self.user_repository.get_one(
            {'email': email_schema.recipient}
        )
        if not user:
            raise HTTPException(
                status_code=400,
                detail='User not found'
            )
        settings = get_settings()

        to_encode = {'sub': email_schema.recipient}

        verification_token_expire_delta = timedelta(
            minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES
        )
        verification_to_encode = to_encode.copy()

        verification_token = await self.create_token(
            verification_to_encode,
            verification_token_expire_delta
        )

        verification_url = (
            f'{settings.BASE_URL}/auth/reset-password?verification_token'
            f'={verification_token}'
        )

        email_schema = EmailCreatePayloadSchema(
            **email_schema.model_dump(),
            subject='YOUR URL',
            body=f'Your verification url is {verification_url}',
        )

        return await self.email_service.send_email(
            email_schema
        )

    async def reset_password(
            self,
            user_id: int,
            new_password_data: PasswordCreationMixin
    ) -> bool:
        new_password_data.password = await get_password_hash(
            new_password_data.password
        )

        await self.user_service.user_repository.update(
            user_id,
            new_password_data
        )

        return True

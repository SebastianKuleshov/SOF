from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from jwcrypto.common import JWException
from keycloak import KeycloakAuthenticationError, KeycloakPostError

from app.auth.repositories import AuthRepository
from app.auth.schemas import TokenBaseSchema, EmailCreateSchema
from app.dependencies import keycloak_openid, keycloak_admin
from app.dependencies import oauth2_scheme
from app.users.repositories import UserRepository
from app.users.schemas import UserOutSchema, UserInRequestSchema


class AuthService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            auth_repository: Annotated[AuthRepository, Depends()],
    ) -> None:
        self.user_repository = user_repository
        self.auth_repository = auth_repository

    @staticmethod
    async def get_user_id_from_request(request: Request) -> str:
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
            token: str = Depends(oauth2_scheme)
    ) -> UserOutSchema | None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            payload = await keycloak_openid.a_decode_token(token)

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

        except JWException:
            raise credentials_exception

        user = await user_repository.get_by_id_with_roles(user_id)
        if user is None:
            raise credentials_exception
        user_permissions = await user_repository.get_user_permissions(user_id)

        request.state.user_id = user_id
        user_schema = UserInRequestSchema.model_validate(
            {
                **user.__dict__,
                'permissions': user_permissions
            }
        )
        request.state.user = user_schema
        return UserOutSchema.model_validate(user)

    async def login(
            self,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenBaseSchema:
        try:
            tokens = await keycloak_openid.a_token(
                form_data.username,
                form_data.password
            )
        except KeycloakAuthenticationError:
            raise HTTPException(
                status_code=400,
                detail='Invalid user credentials'
            )
        access_token = tokens.get('access_token')
        payload = await keycloak_openid.a_decode_token(access_token)
        user_id = payload.get('sub')
        await self.auth_repository.create_token(user_id, access_token)
        return tokens

    async def refresh(
            self,
            refresh_token: str
    ) -> TokenBaseSchema:
        try:
            tokens = await keycloak_openid.a_refresh_token(refresh_token)
        except KeycloakPostError:
            raise HTTPException(
                status_code=400,
                detail='Invalid refresh token'
            )
        payload = jwt.decode(
            refresh_token, options={'verify_signature': False}
        )
        user_id = payload.get('sub')
        await self.auth_repository.delete_user_tokens(user_id)
        await self.auth_repository.create_token(
            user_id,
            tokens.get('access_token')
        )
        return tokens

    async def logout(
            self,
            refresh_token: str
    ) -> bool:
        await keycloak_openid.a_logout(refresh_token)
        payload = jwt.decode(
            refresh_token, options={'verify_signature': False}
        )
        user_id = payload.get('sub')
        await self.auth_repository.delete_user_tokens(user_id)
        return True

    async def forgot_password(
            self,
            email_schema: EmailCreateSchema
    ) -> bool:

        user = await self.user_repository.get_one(
            {'email': email_schema.recipient}
        )

        try:
            await keycloak_admin.a_send_update_account(
                user.id, ['UPDATE_PASSWORD']
            )
        except KeycloakPostError:
            raise HTTPException(
                status_code=400,
                detail='Failed to send update account'
            )

        return True

    @staticmethod
    def require_permissions(
            required_permissions: set[str]
    ) -> callable:
        def check_permissions(
                request: Request
        ) -> bool:
            user = request.state.user

            user_permissions = user.permissions

            if not required_permissions.issubset(user_permissions):
                raise HTTPException(
                    status_code=403,
                    detail='Permission denied'
                )
            return True

        return check_permissions

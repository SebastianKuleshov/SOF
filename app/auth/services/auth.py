from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from jwcrypto.common import JWException

from app.auth.repositories import AuthRepository
from app.auth.schemas import TokenBaseSchema, EmailCreateSchema
from app.common.services import KeycloakService
from app.dependencies import oauth2_scheme
from app.roles.repositories import RoleRepository
from app.users.repositories import UserRepository
from app.users.schemas import UserOutSchema, UserInRequestSchema, \
    UserCreatePayloadSchema, UserCreateSchema


class AuthService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            auth_repository: Annotated[AuthRepository, Depends()],
            role_repository: Annotated[RoleRepository, Depends()],
            keycloak_service: Annotated[KeycloakService, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.auth_repository = auth_repository
        self.role_repository = role_repository
        self.keycloak_service = keycloak_service

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
            keycloak_service: Annotated[KeycloakService, Depends()],
            token: str = Depends(oauth2_scheme)
    ) -> UserOutSchema | None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            payload = await keycloak_service.decode_token(token)

            external_user_id = payload.get('sub')
            user = await user_repository.get_one(
                {'external_id': external_user_id}
            )
            token_exists = await auth_repository.check_token(
                external_user_id,
                token
            )
            if not token_exists:
                await auth_repository.delete_user_tokens(external_user_id)
                raise HTTPException(
                    status_code=400,
                    detail='Token is invalid'
                )

            if user.id is None:
                raise credentials_exception

        except JWException:
            raise credentials_exception

        user = await user_repository.get_by_id_with_roles(user.id)
        if user is None:
            raise credentials_exception
        user_permissions = await user_repository.get_user_permissions(user.id)

        request.state.user_id = user.id
        user_schema = UserInRequestSchema.model_validate(
            {
                **user.__dict__,
                'permissions': user_permissions
            }
        )
        request.state.user = user_schema
        return UserOutSchema.model_validate(user)

    async def sign_up(
            self,
            user_schema: UserCreateSchema
    ) -> UserOutSchema:

        if await self.user_repository.get_one(
                {'email': user_schema.email}
        ) is not None:
            raise HTTPException(
                status_code=400,
                detail='Email already exists'
            )

        external_user_id = await self.keycloak_service.create_user(user_schema)

        user = UserCreatePayloadSchema(
            **user_schema.model_dump(),
            external_id=external_user_id,
            password=user_schema.password,
            repeat_password=user_schema.password
        )

        user_model = await self.user_repository.create(user)

        roles = await self.role_repository.get_roles_by_name(['user'])
        await self.user_repository.attach_roles_to_user(
            user_model.id,
            roles
        )

        return UserOutSchema.model_validate(user_model)

    async def login(
            self,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenBaseSchema:
        tokens = await self.keycloak_service.get_tokens_by_user_credentials(
            form_data
        )
        access_token = tokens.get('access_token')
        payload = await self.keycloak_service.decode_token(access_token)
        external_user_id = payload.get('sub')
        await self.auth_repository.create_token(external_user_id, access_token)
        return TokenBaseSchema.model_validate(tokens)

    async def refresh(
            self,
            refresh_token: str
    ) -> TokenBaseSchema:
        tokens = await self.keycloak_service.refresh_token(refresh_token)
        payload = jwt.decode(
            refresh_token, options={'verify_signature': False}
        )
        external_user_id = payload.get('sub')
        await self.auth_repository.delete_user_tokens(external_user_id)
        await self.auth_repository.create_token(
            external_user_id,
            tokens.get('access_token')
        )
        return TokenBaseSchema.model_validate(tokens)

    async def logout(
            self,
            refresh_token: str
    ) -> bool:
        await self.keycloak_service.logout(refresh_token)
        payload = jwt.decode(
            refresh_token, options={'verify_signature': False}
        )
        external_user_id = payload.get('sub')
        await self.auth_repository.delete_user_tokens(external_user_id)
        return True

    async def forgot_password(
            self,
            email_schema: EmailCreateSchema
    ) -> bool:

        user = await self.user_repository.get_one(
            {'email': email_schema.recipient}
        )

        if user is None:
            raise HTTPException(
                status_code=400,
                detail='User not found'
            )

        await self.keycloak_service.send_update_account(
            user.external_id,
            ['UPDATE_PASSWORD']
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

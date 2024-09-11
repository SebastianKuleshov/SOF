from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from keycloak import KeycloakPostError, KeycloakAuthenticationError

from app.auth.schemas import TokenBaseSchema, DecodedTokenBaseSchema
from app.dependencies import keycloak_openid, keycloak_admin
from app.users.schemas import UserCreateSchema


class KeycloakService:
    keycloak_openid = keycloak_openid
    keycloak_admin = keycloak_admin

    @classmethod
    async def create_user(
            cls,
            user_schema: UserCreateSchema
    ) -> int:
        try:
            return await cls.keycloak_admin.a_create_user(
                {
                    'email': user_schema.email,
                    'username': user_schema.nick_name,
                    'enabled': True,
                    'emailVerified': False,
                    'credentials': [
                        {
                            'type': 'password',
                            'value': user_schema.password,
                            'temporary': False
                        }
                    ]
                }
            )
        except KeycloakPostError:
            raise HTTPException(
                status_code=400,
                detail='Failed to create user in Keycloak'
            )

    @classmethod
    async def get_tokens_by_user_credentials(
            cls,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenBaseSchema:
        try:
            tokens_data = await cls.keycloak_openid.a_token(
                form_data.username,
                form_data.password
            )
            return TokenBaseSchema.model_validate(tokens_data)
        except KeycloakAuthenticationError:
            raise HTTPException(
                status_code=400,
                detail='Invalid user credentials'
            )

    @classmethod
    async def decode_token(
            cls,
            token: str
    ) -> DecodedTokenBaseSchema:
        decoded = await cls.keycloak_openid.a_decode_token(token)
        return DecodedTokenBaseSchema.model_validate(decoded)

    @classmethod
    async def refresh_token(
            cls,
            refresh_token: str
    ) -> TokenBaseSchema:
        try:
            tokens_data = await keycloak_openid.a_refresh_token(refresh_token)
            return TokenBaseSchema.model_validate(tokens_data)
        except KeycloakPostError:
            raise HTTPException(
                status_code=400,
                detail='Invalid refresh token'
            )

    @classmethod
    async def logout(
            cls,
            refresh_token: str
    ) -> bool:
        await keycloak_openid.a_logout(refresh_token)
        return True

    @classmethod
    async def update_account(
            cls,
            external_id: str,
            data: dict
    ) -> None:
        try:
            await cls.keycloak_admin.a_update_user(external_id, data)
        except KeycloakPostError:
            raise HTTPException(
                status_code=400,
                detail='Failed to update account'
            )

    @classmethod
    async def send_update_account(
            cls,
            external_id: str,
            required_actions: list
    ) -> bool:
        try:
            await cls.keycloak_admin.a_send_update_account(
                external_id,
                required_actions
            )
        except KeycloakPostError:
            raise HTTPException(
                status_code=400,
                detail='Failed to send update account'
            )

        return True

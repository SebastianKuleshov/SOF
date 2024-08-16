from typing import Annotated

from aioredis import Redis
from fastapi import Depends

from app.auth.schemas import EmailCreatePayloadSchema
from app.core.adapters.email.email_adapter import get_email_adapter, \
    EmailAdapter
from app.core.adapters.redis.redis_adapter import get_session


class AuthRepository:
    def __init__(
            self,
            redis: Annotated[Redis, Depends(get_session)],
            email: Annotated[EmailAdapter, Depends(get_email_adapter)]
    ) -> None:
        self.redis = redis
        self.email = email

    async def create_tokens(
            self,
            user_id: int,
            refresh_token: str,
            access_token: str
    ) -> bool:
        key = str(user_id)
        await self.redis.rpush(key, refresh_token, access_token)
        return True

    async def check_token(
            self,
            user_id: int,
            token: str
    ) -> bool:
        key = str(user_id)
        tokens = await self.redis.lrange(key, 0, -1)
        return token.encode() in tokens

    async def delete_user_token(
            self,
            user_id: int,
            token: str
    ) -> bool:
        key = str(user_id)
        return await self.redis.lrem(key, 0, token.encode())

    async def delete_user_tokens(
            self,
            user_id: int
    ) -> bool:
        key = str(user_id)
        return await self.redis.delete(key)

    async def send_email(
            self,
            email_schema: EmailCreatePayloadSchema
    ) -> bool:
        return await self.email.send_email(
            email_schema.subject,
            email_schema.recipient,
            email_schema.body,
        )

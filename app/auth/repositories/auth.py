from typing import Annotated

from aioredis import Redis
from fastapi import Depends

from app.core.adapters.redis.redis_adapter import get_session


class AuthRepository:
    def __init__(
            self,
            redis: Annotated[Redis, Depends(get_session)]
    ) -> None:
        self.redis = redis

    async def create(
            self,
            user_id: int,
            refresh_token: str,
            access_token: str
    ) -> bool:
        key = str(user_id)
        await self.redis.rpush(key, refresh_token)
        await self.redis.rpush(key, access_token)
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

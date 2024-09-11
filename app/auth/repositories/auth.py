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

    async def create_token(
            self,
            user_id: str,
            token: str
    ) -> bool:
        await self.redis.rpush(user_id, token)
        return True

    async def check_token(
            self,
            user_id: str,
            token: str
    ) -> bool:
        tokens = await self.redis.lrange(user_id, 0, -1)
        return token.encode() in tokens

    async def delete_user_tokens(
            self,
            user_id: str
    ) -> bool:
        return await self.redis.delete(user_id)

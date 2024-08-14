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
            token: str
    ) -> bool:
        key = f'{user_id}:{token}'
        return await self.redis.set(key, 0)

    async def get(
            self,
            user_id: int,
            token: str
    ) -> str:
        key = f'{user_id}:{token}'
        return await self.redis.get(key)

    async def delete_user_token(
            self,
            user_id: int,
            token: str
    ) -> bool:
        key = f'{user_id}:{token}'
        return await self.redis.delete(key)

    async def delete_user_tokens(
            self,
            user_id: int
    ) -> bool:
        keys = await self.redis.keys(f'{user_id}:*')
        for key in keys:
            await self.redis.delete(key)
        return True

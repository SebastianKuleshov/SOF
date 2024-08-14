from aioredis import from_url

from app.dependencies import get_settings

settings = get_settings()

session = from_url(settings.REDIS_URL)


async def get_session():
    async with session as conn:
        yield conn

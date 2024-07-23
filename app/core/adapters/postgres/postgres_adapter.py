from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.dependencies import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


class Base(DeclarativeBase):
    pass

from functools import lru_cache

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


async def get_password_hash(
        password
):
    return pwd_context.hash(password)


async def verify_password(
        plain_password,
        hashed_password
):
    return pwd_context.verify(plain_password, hashed_password)

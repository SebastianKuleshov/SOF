from functools import lru_cache

from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenIDConnection, KeycloakAdmin
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


settings = get_settings()

keycloak_openid = KeycloakOpenIDConnection(
    server_url=settings.KEYCLOAK_SERVER_URL,
    realm_name='SOF',
    user_realm_name='master',
    client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
    client_secret_key=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
    username='root',
    password='string3!G',
    verify=True
)

keycloak_admin = KeycloakAdmin(
    connection=keycloak_openid
)



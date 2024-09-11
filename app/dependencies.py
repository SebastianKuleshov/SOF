from functools import lru_cache

from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenIDConnection, KeycloakAdmin, KeycloakOpenID
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

keycloak_openid_connection = KeycloakOpenIDConnection(
    server_url=settings.KEYCLOAK_SERVER_URL,
    realm_name=settings.KEYCLOAK_REALM,
    user_realm_name=settings.KEYCLOAK_MASTER_REALM,
    client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
    client_secret_key=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
    username=settings.SUPERUSER_USERNAME,
    password=settings.SUPERUSER_PASSWORD,
    verify=True
)

keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_SERVER_URL,
    realm_name=settings.KEYCLOAK_REALM,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
    verify=True
)

keycloak_admin = KeycloakAdmin(
    connection=keycloak_openid_connection
)

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ALLOW_ORIGINS: str
    BASE_URL: str
    EMAIL_SMTP_HOST: str
    EMAIL_SMTP_PORT: int
    EMAIL_SMTP_TLS: bool
    EMAIL_SMTP_USERNAME: str
    EMAIL_SMTP_PASSWORD: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str
    AWS_BUCKET_URL: str
    ALLOWED_IMAGE_TYPES: list[str]
    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_ADMIN_CLIENT_ID: str
    KEYCLOAK_ADMIN_CLIENT_SECRET: str
    KEYCLOAK_REALM: str
    KEYCLOAK_MASTER_REALM: str
    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_EMAIL: str
    TIMEZONE: str

    class Config:
        env_file = './app/.env'
        extra = 'ignore'

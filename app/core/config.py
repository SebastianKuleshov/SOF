from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ALLOW_ORIGINS: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int
    EMAIL_SMTP_HOST: str
    EMAIL_SMTP_PORT: int
    EMAIL_SMTP_TLS: bool
    EMAIL_SMTP_USERNAME: str
    EMAIL_SMTP_PASSWORD: str
    BASE_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str
    AWS_BUCKET_URL: str
    ALLOWED_IMAGE_TYPES: list[str]


    class Config:
        env_file = './app/.env'
        extra = 'ignore'

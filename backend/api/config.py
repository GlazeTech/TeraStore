import os
from functools import lru_cache

from pydantic_settings import BaseSettings


def get_env_var(var_name: str) -> str:
    try:
        value = os.environ[var_name]
    except KeyError as exc:
        msg = f"Environment variable {var_name} is not set"
        raise ValueError(msg) from exc
    return value


class Settings(BaseSettings):
    PROJECT_NAME: str = "TeraStore API"
    DATABASE_URL: str = get_env_var("DATABASE_URL")
    TERASTORE_ADMIN_USERNAME: str = get_env_var("TERASTORE_ADMIN_USERNAME")
    TERASTORE_ADMIN_PASSWORD: str = get_env_var("TERASTORE_ADMIN_PASSWORD")
    ALLOWED_ORIGINS: str = get_env_var(
        "ALLOWED_ORIGINS",  # comma-separated list of allowed origins
    )


class AuthSettings(BaseSettings):
    TERASTORE_JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100
    REFRESH_TOKEN_COOKIE_NAME: str = "terastore_refresh_token"
    REFRESH_ENDPOINT: str = "/auth/refresh"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()

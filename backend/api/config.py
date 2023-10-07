import os

from pydantic import BaseSettings, PostgresDsn


def get_database_uri() -> str:
    """Get the database URI from the environment."""
    uri = PostgresDsn(os.getenv("DATABASE_URI"))
    if uri is None:
        msg = "DATABASE_URI is not set"
        raise ValueError(msg)
    return str(uri)


def get_secret_key() -> str:
    """Get the secret key from the environment."""
    key = os.getenv("SECRET_KEY")
    if key is None:
        msg = "SECRET_KEY is not set"
        raise ValueError(msg)
    return key


class Settings(BaseSettings):
    """Application settings."""

    ENV = "dev" if os.getenv("ENV") == "dev" else "prod"
    PROJECT_NAME: str = f"TeraStore API - {ENV.capitalize()}"
    DESCRIPTION: str = "TeraStore API"
    VERSION: str = "0.1.0"
    SECRET_KEY: str = get_secret_key()
    DATABASE_URI: str = get_database_uri()


settings = Settings()

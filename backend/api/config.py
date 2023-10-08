import os

from pydantic import BaseSettings


def get_database_uri() -> str:
    """Get the database URI from the environment."""
    uri = os.getenv("DATABASE_URI")
    if uri is None:
        msg = "DATABASE_URI is not set"
        raise ValueError(msg)
    return str(uri)


def get_database_username() -> str:
    """Get the database username from the environment."""
    username = os.getenv("DATABASE_USERNAME")
    if username is None:
        msg = "DATABASE_USERNAME is not set"
        raise ValueError(msg)
    return username


def get_database_password() -> str:
    """Get the database password from the environment."""
    password = os.getenv("DATABASE_PASSWORD")
    if password is None:
        msg = "DATABASE_PASSWORD is not set"
        raise ValueError(msg)
    return password


class Settings(BaseSettings):
    """Application settings."""

    ENV = "dev" if os.getenv("ENV") == "dev" else "prod"
    PROJECT_NAME: str = f"TeraStore API - {ENV.capitalize()}"
    DESCRIPTION: str = "TeraStore API"
    VERSION: str = "0.1.0"
    DATABASE_URI: str = get_database_uri()
    DATABASE_USERNAME: str = get_database_username()
    DATABASE_PASSWORD: str = get_database_password()


settings = Settings()

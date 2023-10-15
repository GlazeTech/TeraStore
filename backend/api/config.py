import os
from functools import lru_cache

from pydantic import BaseSettings


def get_env_var(var_name: str) -> str:
    """Get the environment variable or return exception.

    Args:
    ----
        var_name (str): The name of the environment variable.

    Returns:
    -------
        The value of the environment variable.
    """
    value = os.getenv(var_name)
    if value is None:
        msg = f"Environment variable {var_name} is not set"
        raise ValueError(msg)
    return value


class Settings(BaseSettings):
    """Application settings."""

    ENV = get_env_var("ENV")
    PROJECT_NAME = f"TeraStore API - {ENV}"
    DATABASE_URL = get_env_var("DATABASE_URL")
    API_URL = "0.0.0.0" if ENV == "dev" else get_env_var("API_URL")  # noqa: S104
    API_PORT = 8000 if ENV == "dev" else int(get_env_var("API_PORT"))


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    return Settings()

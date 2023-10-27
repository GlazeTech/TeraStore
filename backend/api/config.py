import os
from functools import lru_cache

from pydantic import BaseSettings


def get_env_var(var_name: str) -> str:
    try:
        value = os.environ[var_name]
    except KeyError as exc:
        msg = f"Environment variable {var_name} is not set"
        raise ValueError(msg) from exc
    return value


class Settings(BaseSettings):
    PROJECT_NAME = "TeraStore API"
    DATABASE_URL = get_env_var("DATABASE_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()

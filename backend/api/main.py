from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.config import settings
from api.database import create_db_and_tables, drop_tables
from api.public import api as public_api
from api.utils.mock_data_generator import create_devices_and_pulses


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create and drop the database and tables for testing purposes."""
    create_db_and_tables()
    create_devices_and_pulses()
    yield
    drop_tables()


def create_app() -> FastAPI:
    """Create a FastAPI application."""
    app = FastAPI(lifespan=lifespan) if settings.ENV == "dev" else FastAPI()

    app.include_router(public_api)

    return app

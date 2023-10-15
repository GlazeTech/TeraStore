from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings
from api.database import create_db_and_tables, drop_tables
from api.public import make_api
from api.utils.mock_data_generator import create_devices_and_pulses


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create and drop the database and tables for testing purposes.

    Args:
    ----
        app (FastAPI): The FastAPI application.

    Yields:
    ------
        None
    """
    create_db_and_tables()
    create_devices_and_pulses()
    yield
    drop_tables()


def create_app() -> FastAPI:
    """Create a FastAPI application.

    Returns
    -------
        A FastAPI application.
    """
    settings = get_settings()
    app = FastAPI(lifespan=lifespan) if settings.ENV == "dev" else FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root() -> dict[str, str]:
        """Return a simple message.

        Returns
        -------
            A simple message.
        """
        return {"message": "Hello from FastAPI!"}

    app.include_router(make_api())

    return app

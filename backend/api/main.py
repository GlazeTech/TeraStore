from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import _create_db_and_tables, _drop_tables
from api.public import make_api
from api.utils.mock_data_generator import create_devices_and_pulses
from api.utils.types import WithLifespan


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create and drop the database and tables for testing purposes.

    Args:
    ----
        app (FastAPI): The FastAPI application.

    Yields:
    ------
        None
    """
    _create_db_and_tables()
    create_devices_and_pulses()
    yield
    _drop_tables()


def _create_app(with_lifespan: WithLifespan) -> FastAPI:
    """Create a FastAPI application.

    Returns
    -------
        A FastAPI application.
    """
    app = FastAPI(lifespan=_lifespan) if with_lifespan.value else FastAPI()
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

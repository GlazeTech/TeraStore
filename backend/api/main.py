import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import create_db_and_tables, drop_tables
from api.public import make_api
from api.utils.logging import EndpointFilter
from api.utils.mock_data_generator import (
    create_devices_and_pulses,
    create_frontend_dev_data,
)
from api.utils.types import Lifespan


@asynccontextmanager
async def lifespan_dev(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    create_devices_and_pulses()
    create_frontend_dev_data()
    yield
    drop_tables()


@asynccontextmanager
async def lifespan_prod(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield


LIFESPAN_FUNCTIONS = {
    Lifespan.PROD: lifespan_prod,
    Lifespan.DEV: lifespan_dev,
    Lifespan.TEST: lifespan_dev,
}


def create_app(lifespan: Lifespan) -> FastAPI:
    app = FastAPI(lifespan=LIFESPAN_FUNCTIONS[lifespan])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(EndpointFilter(path="/health"))

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "Hello from FastAPI!"}

    app.include_router(make_api())

    return app

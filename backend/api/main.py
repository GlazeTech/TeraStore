from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import create_db_and_tables, drop_tables
from api.public import make_api
from api.utils.mock_data_generator import create_devices_and_pulses
from api.utils.types import WithLifespan


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    create_devices_and_pulses()
    yield
    drop_tables()


def create_app(with_lifespan: WithLifespan) -> FastAPI:
    app = FastAPI(lifespan=lifespan) if with_lifespan.value else FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "Hello from FastAPI!"}

    app.include_router(make_api())

    return app

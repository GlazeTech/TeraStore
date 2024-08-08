import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from api.config import get_settings
from api.database import app_engine, create_db_and_tables, drop_tables
from api.public import make_api
from api.public.auth.crud import create_user
from api.public.auth.models import AuthLevel, UserCreate
from api.utils.exception_handlers import exception_handlers_factory
from api.utils.exceptions import UserAlreadyExistsError
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
    settings = get_settings()
    create_db_and_tables()

    # On first run, create admin user
    try:
        with Session(app_engine) as session:
            create_user(
                UserCreate(
                    email=settings.TERASTORE_ADMIN_USERNAME,
                    password=settings.TERASTORE_ADMIN_PASSWORD,
                ),
                auth_level=AuthLevel.ADMIN,
                db=session,
            )
    except UserAlreadyExistsError:
        pass
    yield


@asynccontextmanager
async def lifespan_integration_test(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()

    # Populate DB on first test run - pass if already populated
    try:
        create_devices_and_pulses()
        create_frontend_dev_data()
    except IntegrityError:
        pass
    yield
    drop_tables()


LIFESPAN_FUNCTIONS = {
    Lifespan.PROD: lifespan_prod,
    Lifespan.DEV: lifespan_dev,
    Lifespan.TEST: None,
    Lifespan.INTEGRATION_TEST: lifespan_integration_test,
}


def create_app(lifespan: Lifespan) -> FastAPI:
    settings = get_settings()
    app = FastAPI(lifespan=LIFESPAN_FUNCTIONS[lifespan])
    app.add_middleware(
        CORSMiddleware,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
    )

    for exc, handler in exception_handlers_factory():
        app.add_exception_handler(exc, handler)

    # Add logging filters
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(EndpointFilter(path="/health"))

    app.include_router(make_api())

    return app

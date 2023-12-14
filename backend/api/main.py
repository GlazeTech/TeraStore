import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from api.database import create_db_and_tables, drop_tables
from api.public import make_api
from api.utils.exception_handlers import (
    attr_data_type_does_not_exist_exception_handler,
    attr_data_type_exists_exception_handler,
    attr_key_does_not_exist_exception_handler,
    credentials_incorrect_exception_handler,
    device_not_found_exception_handler,
    pulse_column_nonexistent_exception_handler,
    pulse_not_found_exception_handler,
    username_already_exists_exception_handler,
    username_or_password_incorrect_exception_handler,
)
from api.utils.exceptions import (
    AttrDataTypeDoesNotExistError,
    AttrDataTypeExistsError,
    AttrKeyDoesNotExistError,
    CredentialsIncorrectError,
    DeviceNotFoundError,
    EmailOrPasswordIncorrectError,
    PulseColumnNonexistentError,
    PulseNotFoundError,
    UserAlreadyExistsError,
)
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
    app = FastAPI(lifespan=LIFESPAN_FUNCTIONS[lifespan])
    app.add_middleware(
        CORSMiddleware,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_origins=[
            "http://0.0.0.0:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
    )

    # Add exception handlers
    app.add_exception_handler(
        PulseNotFoundError,
        pulse_not_found_exception_handler,
    )
    app.add_exception_handler(
        DeviceNotFoundError,
        device_not_found_exception_handler,
    )
    app.add_exception_handler(
        AttrDataTypeExistsError,
        attr_data_type_exists_exception_handler,
    )
    app.add_exception_handler(
        AttrKeyDoesNotExistError,
        attr_key_does_not_exist_exception_handler,
    )
    app.add_exception_handler(
        AttrDataTypeDoesNotExistError,
        attr_data_type_does_not_exist_exception_handler,
    )
    app.add_exception_handler(
        PulseColumnNonexistentError,
        pulse_column_nonexistent_exception_handler,
    )
    app.add_exception_handler(
        EmailOrPasswordIncorrectError,
        username_or_password_incorrect_exception_handler,
    )
    app.add_exception_handler(
        UserAlreadyExistsError,
        username_already_exists_exception_handler,
    )
    app.add_exception_handler(
        CredentialsIncorrectError,
        credentials_incorrect_exception_handler,
    )

    # Add logging filters
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(EndpointFilter(path="/health"))

    app.include_router(make_api())

    return app

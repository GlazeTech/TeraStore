from collections.abc import Mapping

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette import status
from starlette.types import ExceptionHandler

from api.utils.exceptions import (
    AttrDataTypeDoesNotExistError,
    AttrDataTypeExistsError,
    AttrKeyDoesNotExistError,
    CredentialsIncorrectError,
    DeviceExistsError,
    DeviceNotFoundError,
    EmailOrPasswordIncorrectError,
    InvalidSerialNumberError,
    PulseColumnNonexistentError,
    PulseNotFoundError,
    UserAlreadyExistsError,
)


def exc_handler(
    status_code: int, headers: Mapping[str, str] | None = None
) -> ExceptionHandler:
    async def exception_handler(_request: Request, exc: Exception) -> Response:
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc)},
            headers=headers,
        )

    return exception_handler


def exception_handlers_factory() -> list[tuple[type[Exception], ExceptionHandler]]:
    return [
        (PulseNotFoundError, exc_handler(status.HTTP_404_NOT_FOUND)),
        (DeviceNotFoundError, exc_handler(status.HTTP_404_NOT_FOUND)),
        (DeviceExistsError, exc_handler(status.HTTP_409_CONFLICT)),
        (InvalidSerialNumberError, exc_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)),
        (AttrDataTypeExistsError, exc_handler(status.HTTP_400_BAD_REQUEST)),
        (AttrKeyDoesNotExistError, exc_handler(status.HTTP_404_NOT_FOUND)),
        (AttrDataTypeDoesNotExistError, exc_handler(status.HTTP_404_NOT_FOUND)),
        (PulseColumnNonexistentError, exc_handler(status.HTTP_404_NOT_FOUND)),
        (EmailOrPasswordIncorrectError, exc_handler(status.HTTP_401_UNAUTHORIZED)),
        (UserAlreadyExistsError, exc_handler(status.HTTP_409_CONFLICT)),
        (
            CredentialsIncorrectError,
            exc_handler(
                status.HTTP_401_UNAUTHORIZED, headers={"WWW-Authenticate": "Bearer"}
            ),
        ),
    ]

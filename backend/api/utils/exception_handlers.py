from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from api.utils.exceptions import (
    AttrDataTypeDoesNotExistError,
    AttrDataTypeExistsError,
    AttrKeyDoesNotExistError,
    CredentialsIncorrectError,
    DeviceNotFoundError,
    PulseColumnNonexistentError,
    PulseNotFoundError,
)


async def pulse_not_found_exception_handler(
    _request: Request,
    exc: PulseNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def pulse_column_nonexistent_exception_handler(
    _request: Request,
    exc: PulseColumnNonexistentError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def device_not_found_exception_handler(
    _request: Request,
    exc: DeviceNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def attr_data_type_exists_exception_handler(
    _request: Request,
    exc: AttrDataTypeExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def attr_key_does_not_exist_exception_handler(
    _request: Request,
    exc: AttrKeyDoesNotExistError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def attr_data_type_does_not_exist_exception_handler(
    _request: Request,
    exc: AttrDataTypeDoesNotExistError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def username_or_password_incorrect_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
    )


async def username_already_exists_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


async def credentials_incorrect_exception_handler(
    _request: Request,
    exc: CredentialsIncorrectError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )

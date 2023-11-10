from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from api.utils.exceptions import (
    AttrDataConversionError,
    AttrDataTypeUnsupportedError,
    AttrKeyNotFoundError,
    DeviceNotFoundError,
    PulseNotFoundError,
)


async def attr_data_type_unsupported_exception_handler(
    _request: Request,
    exc: AttrDataTypeUnsupportedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def attr_data_conversion_exception_handler(
    _request: Request,
    exc: AttrDataConversionError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


async def attr_key_not_found_exception_handler(
    _request: Request,
    exc: AttrKeyNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


async def pulse_not_found_exception_handler(
    _request: Request,
    exc: PulseNotFoundError,
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

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from api.utils.exceptions import DeviceNotFoundError, PulseNotFoundError


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

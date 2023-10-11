from fastapi import APIRouter

from api.public.device import views as devices
from api.public.pulse import views as pulses


def make_api() -> APIRouter:
    """Create the public API router."""
    api = APIRouter()
    api.include_router(pulses.router, prefix="/pulses", tags=["Pulses"])
    api.include_router(devices.router, prefix="/devices", tags=["Devices"])
    return api

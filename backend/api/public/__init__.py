from fastapi import APIRouter, Depends

from api.public.attrs import views as eav
from api.public.auth import views as auth
from api.public.auth.auth_handler import get_current_user
from api.public.device import views as devices
from api.public.health import views as health
from api.public.pulse import views as pulses
from api.public.user import views as user

PROTECTED = [Depends(get_current_user)]


def make_api() -> APIRouter:
    """Create the public API router."""
    api = APIRouter()
    api.include_router(
        pulses.router,
        prefix="/pulses",
        tags=["Pulses"],
        dependencies=PROTECTED,
    )
    api.include_router(
        devices.router,
        prefix="/devices",
        tags=["Devices"],
        dependencies=PROTECTED,
    )
    api.include_router(
        eav.router,
        prefix="/attrs",
        tags=["Attrs"],
        dependencies=PROTECTED,
    )
    api.include_router(
        user.router,
        prefix="/user",
        tags=["User"],
        dependencies=PROTECTED,
    )
    api.include_router(health.router, prefix="/health", tags=["Health"])
    api.include_router(auth.router, prefix="/auth", tags=["Auth"])
    return api

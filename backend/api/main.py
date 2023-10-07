from fastapi import FastAPI

from api.public import api as public_api


def create_app() -> FastAPI:
    """Create a FastAPI application."""
    app = FastAPI()

    app.include_router(public_api)

    return app

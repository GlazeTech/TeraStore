import uvicorn

from api.config import get_settings
from api.main import create_app

api = create_app()

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "asgi:api",
        host=settings.API_URL,
        port=settings.API_PORT,
        reload=settings.ENV == "dev",
    )

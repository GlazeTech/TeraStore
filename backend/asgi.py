import argparse

import uvicorn

from api.config import get_settings
from api.main import create_app
from api.utils.types import WithLifespan

parser = argparse.ArgumentParser(description="Start the FastAPI application.")
parser.add_argument(
    "--with-lifespan",
    action="store_true",
    help="Run the lifespan function on startup.",
)
parser.add_argument(
    "--with-reload",
    action="store_true",
    help="Run the application with auto-reload.",
)
args = parser.parse_args()

if args.with_lifespan:
    api = create_app(WithLifespan.TRUE)
else:
    api = create_app(WithLifespan.FALSE)


if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "asgi:api",
        host=settings.API_URL,
        port=settings.API_PORT,
        reload=args.with_reload,
    )

import argparse

import uvicorn

from api.config import get_settings
from api.main import create_app
from api.utils.types import Lifespan

parser = argparse.ArgumentParser(description="Start the FastAPI application.")

parser.add_argument(
    "--lifespan",
    choices=[lifespan.name for lifespan in Lifespan],
    help="Run the application with the lifespan PROD, DEV or TEST.",
    required=True,
)
parser.add_argument(
    "--with-reload",
    action="store_true",
    help="Run the application with auto-reload.",
)
args = parser.parse_args()

api = create_app(Lifespan[args.lifespan])


if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "asgi:api",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=args.with_reload,
    )

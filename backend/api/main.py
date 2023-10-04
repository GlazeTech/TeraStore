import os

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    """Return a simple message."""
    return {"message": "Hello World"}


def start() -> None:
    """Start server."""
    uvicorn.run("api.main:app", port=8000, reload=os.getenv("ENV") == "dev")

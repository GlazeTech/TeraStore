import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Return a simple message."""
    return {"message": "Hello from FastAPI!"}


def start() -> None:
    """Start server."""
    uvicorn.run("api.main:app", port=8000, reload=os.getenv("ENV") == "dev")

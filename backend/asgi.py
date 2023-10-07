import uvicorn

from api.main import create_app

api = create_app()

if __name__ == "__main__":
    uvicorn.run("asgi:api", reload=True)

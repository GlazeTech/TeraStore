from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from api.config import get_settings
from api.database import get_session
from api.main import create_app
from api.utils.types import WithLifespan


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """Yield a Session object for interacting with the db."""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, echo=settings.ENV in ("dev", "test"))

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a TestClient instance for testing."""
    app = create_app(WithLifespan.FALSE)

    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

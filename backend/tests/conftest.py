from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from api.config import get_settings
from api.database import create_db_and_tables, drop_tables, get_session
from api.main import create_app
from api.utils.types import WithLifespan


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """Yield a Session object for interacting with the db during tests."""
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, echo=settings.ENV in ("dev", "test"))

    drop_tables(engine)
    create_db_and_tables(engine)

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


@pytest.fixture()
def device_uuid(client: TestClient) -> Generator[str, None, None]:
    """Create a Device for testing purposes."""
    device_payload = {"friendly_name": "Glaze I"}
    response = client.post(
        "/devices/",
        json=device_payload,
    )

    if response.status_code == 200:
        data = response.json()
        yield data["device_id"]  # This will be used in your test functions
    else:
        pytest.fail(f"Failed to create device: {response.status_code}")

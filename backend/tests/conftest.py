from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from api.config import get_settings
from api.database import create_db_and_tables, drop_tables, get_session
from api.main import create_app
from api.public.auth.crud import create_user
from api.public.auth.models import AuthLevel, UserCreate
from api.utils.types import Lifespan


@pytest.fixture(name="db_session")
def setup_db() -> Generator[Session, None, None]:
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL, echo=True)

    create_db_and_tables(engine)

    user = UserCreate(
        email="admin@admin",
        password="admin",
    )

    with Session(engine) as session:
        create_user(
            user,
            auth_level=AuthLevel.ADMIN,
            db=session,
        )

        yield session

    drop_tables(engine)


@pytest.fixture()
def setup_client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app(Lifespan.TEST)

    def get_session_override() -> Session:
        return db_session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client")
def client_fixture_with_access_token(
    setup_client: TestClient,
) -> TestClient:
    """Create a TestClient with an access token for testing purposes."""
    login_payload = {"username": "admin@admin", "password": "admin"}
    response = setup_client.post(
        "/auth/login",
        data=login_payload,
    )

    data = response.json()
    access_token = data["access_token"]

    setup_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return setup_client


@pytest.fixture()
def device_id(client: TestClient) -> Generator[UUID, None, None]:
    """Create a Device for testing purposes."""
    device_payload = {"friendly_name": "Glaze I"}
    response = client.post(
        "/devices/",
        json=device_payload,
    )

    if response.status_code == 200:
        data = response.json()
        yield data["device_id"]
    else:
        pytest.fail(f"Failed to create device: {response.status_code}")

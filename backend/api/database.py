from collections.abc import Iterator

from sqlmodel import Session, create_engine

from api.config import settings

# Below is required for safe use;
# see https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URI, echo=True, connect_args=connect_args)


def get_session() -> Iterator[Session]:
    """Yield a Session object for interacting with the db."""
    with Session(engine) as session:
        yield session

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from api.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, echo=settings.ENV == "dev")


def create_db_and_tables() -> None:
    """Create the database and tables for testing purposes."""
    SQLModel.metadata.create_all(engine)


def drop_tables() -> None:
    """Drop the tables from the database."""
    SQLModel.metadata.drop_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a Session object for interacting with the db."""
    with Session(engine) as session:
        yield session

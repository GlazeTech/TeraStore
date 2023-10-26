from uuid import UUID

from sqlmodel import Field, SQLModel


class PulseStrAttrs(SQLModel, table=True):
    """The purpose of this class is to interact with the database."""

    key: str
    value: str
    pulse_id: UUID = Field(foreign_key="pulse.pulse_id", index=True)

    index: int | None = Field(default=None, primary_key=True)


class PulseKeyRegistry(SQLModel, table=True):
    """Table model for Pulse EAV key registry."""

    key: str = Field(primary_key=True)

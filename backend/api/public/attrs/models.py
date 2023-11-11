from pydantic.types import StrictStr
from sqlmodel import Field, SQLModel


class PulseAttrsBase(SQLModel):
    key: str


class PulseAttrsStr(PulseAttrsBase, table=True):
    """The purpose of this class is to interact with the database."""

    __tablename__ = "pulse_str_attrs"

    value: StrictStr
    pulse_id: int = Field(foreign_key="pulses.pulse_id", index=True)

    index: int | None = Field(default=None, primary_key=True)


class PulseAttrsStrRead(PulseAttrsBase):
    value: StrictStr


class PulseKeyRegistry(SQLModel, table=True):
    """Table model for Pulse EAV key registry."""

    __tablename__ = "pulse_key_registry"

    key: str

    index: int | None = Field(default=None, primary_key=True)

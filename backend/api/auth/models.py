from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class User(UserBase, table=True):
    user_id: UUID = Field(default_factory=uuid4, primary_key=True)

    hashed_password: str


class UserRead(UserBase):
    user_id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

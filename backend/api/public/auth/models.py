from enum import Enum

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class AuthLevel(Enum):
    UNAUTHORIZED = 1
    USER = 2
    ADMIN = 3


class User(SQLModel, table=True):
    __tablename__ = "users"

    email: str = Field(
        default=None,
        nullable=False,
        index=True,
        primary_key=True,
        unique=True,
    )
    auth_level: AuthLevel = AuthLevel.UNAUTHORIZED
    hashed_password: str


class UserRead(BaseModel):
    email: str
    auth_level: AuthLevel


class UserCreate(BaseModel):
    email: str
    password: str


class UserDelete(BaseModel):
    email: str


class UserUpdate(BaseModel):
    email: str
    auth_level: AuthLevel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

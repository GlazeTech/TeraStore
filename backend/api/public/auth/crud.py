from fastapi import Depends
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.database import get_session
from api.public.auth.helpers import get_password_hash
from api.public.auth.models import User, UserCreate
from api.utils.exceptions import (
    UserAlreadyExistsError,
    UsernameOrPasswordIncorrectError,
)


def get_user(email: str, db: Session = Depends(get_session)) -> User:
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        raise UsernameOrPasswordIncorrectError
    return user


def create_user(user: UserCreate, db: Session = Depends(get_session)) -> None:
    user_to_db = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        salt="",
        hash_function="",
    )
    db.add(user_to_db)
    try:
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise UserAlreadyExistsError(user.email) from e
    db.refresh(user_to_db)

from collections.abc import Sequence

from fastapi import Depends
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.database import get_session
from api.public.auth.helpers import get_password_hash
from api.public.auth.models import User, UserCreate, UserDelete, UserRead, UserUpdate
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
    )
    db.add(user_to_db)
    try:
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise UserAlreadyExistsError(user.email) from e
    db.refresh(user_to_db)


def get_users(db: Session = Depends(get_session)) -> Sequence[UserRead]:
    users = db.exec(select(User)).all()
    return [UserRead(email=user.email, auth_level=user.auth_level) for user in users]


def remove_user(user: UserDelete, db: Session = Depends(get_session)) -> None:
    db.delete(get_user(user.email, db=db))
    db.commit()


def update_auth_level(user: UserUpdate, db: Session = Depends(get_session)) -> None:
    user_from_db = get_user(user.email, db=db)
    user_from_db.auth_level = user.auth_level
    db.add(user_from_db)
    db.commit()

from fastapi import Depends
from sqlmodel import Session, select

from api.auth.models import User, UserRead
from api.database import get_session


def get_user(username: str, db: Session = Depends(get_session)) -> User | None:
    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        return None
    return user


def check_user(user: UserRead, db: Session = Depends(get_session)) -> User | None:
    user_in_db = db.exec(select(User).where(User.username == user.username)).first()
    if not user_in_db:
        return None
    return user_in_db

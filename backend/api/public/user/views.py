from collections.abc import Sequence

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.database import get_session
from api.public.auth.crud import get_users, remove_user, update_auth_level
from api.public.auth.models import UserDelete, UserRead, UserUpdate

router = APIRouter()


@router.post("/delete")
def delete_user(user: UserDelete, db: Session = Depends(get_session)) -> str:
    remove_user(user=user, db=db)
    return "User deleted"


@router.post("/update")
def update_user(user: UserUpdate, db: Session = Depends(get_session)) -> str:
    update_auth_level(user=user, db=db)
    return "User updated"


@router.get("/users")
def list_users(db: Session = Depends(get_session)) -> Sequence[UserRead]:
    return get_users(db=db)


@router.post("/logout")
def logout_user() -> None:
    pass

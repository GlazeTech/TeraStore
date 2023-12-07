from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from api.config import get_auth_settings
from api.database import get_session
from api.public.auth.auth_handler import authenticate_user, create_access_token
from api.public.auth.crud import create_user
from api.public.auth.models import Token, UserCreate

router = APIRouter()

auth_settings = get_auth_settings()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token)


@router.post("/signup")
def create_new_user(user: UserCreate, db: Session = Depends(get_session)) -> str:
    create_user(user, db=db)
    return "User created"


@router.post("/delete")
def delete_user() -> None:
    pass


@router.post("/update")
def update_user() -> None:
    pass


@router.post("/list")
def list_users() -> None:
    pass


@router.post("/logout")
def logout_user() -> None:
    pass

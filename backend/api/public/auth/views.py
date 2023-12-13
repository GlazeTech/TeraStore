from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.config import get_auth_settings
from api.database import get_session
from api.public.auth.auth_handler import (
    OAuth2PasswordAndRefreshRequestForm,
    authenticate_user_password,
    authenticate_user_token,
    create_tokens_from_user,
)
from api.public.auth.crud import create_user
from api.public.auth.models import Token, UserCreate

router = APIRouter()

auth_settings = get_auth_settings()


@router.post("/login")
async def login_for_tokens(
    form_data: OAuth2PasswordAndRefreshRequestForm = Depends(),
    db: Session = Depends(get_session),
) -> Token:
    if form_data.grant_type == "refresh_token":
        user = authenticate_user_token(token=form_data.refresh_token, db=db)
    else:
        user = authenticate_user_password(form_data.username, form_data.password, db=db)
    return Token(**create_tokens_from_user(user))


@router.post("/signup")
def create_new_user(user: UserCreate, db: Session = Depends(get_session)) -> str:
    create_user(user, db=db)
    return "User created"

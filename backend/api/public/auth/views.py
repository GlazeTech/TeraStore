from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from api.config import get_auth_settings
from api.database import get_session
from api.public.auth.auth_handler import (
    authenticate_user_password,
    authenticate_user_token,
    create_tokens_from_user,
)
from api.public.auth.crud import create_user
from api.public.auth.models import Token, UserCreate
from api.utils.exceptions import CredentialsIncorrectError

router = APIRouter()

auth_settings = get_auth_settings()


@router.post("/login")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
) -> Token:
    user = authenticate_user_password(form_data.username, form_data.password, db=db)
    access_token = create_tokens_from_user(response, user)
    return Token(access_token=access_token)


@router.post("/refresh")
async def login_for_refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_session),
) -> Token:
    refresh_token = request.cookies.get(auth_settings.REFRESH_TOKEN_COOKIE_NAME)
    if refresh_token is None:
        raise CredentialsIncorrectError
    user = authenticate_user_token(refresh_token, db=db)
    access_token = create_tokens_from_user(response, user)
    return Token(access_token=access_token)


@router.post("/signup")
def create_new_user(user: UserCreate, db: Session = Depends(get_session)) -> str:
    create_user(user, db=db)
    return "User created"

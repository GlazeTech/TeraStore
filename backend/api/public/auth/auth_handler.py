from datetime import timedelta
from typing import Any, Self

from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session

from api.config import get_auth_settings
from api.database import get_session
from api.public.auth.crud import get_user
from api.public.auth.helpers import verify_password
from api.public.auth.models import User
from api.utils.exceptions import (
    CredentialsIncorrectError,
    UsernameOrPasswordIncorrectError,
)
from api.utils.helpers import get_now

auth_settings = get_auth_settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Adapted from https://github.com/tiangolo/fastapi/discussions/8879
class OAuth2PasswordAndRefreshRequestForm(OAuth2PasswordRequestForm):
    def __init__(  # noqa: PLR0913
        self: Self,
        grant_type: str = Form(default=None, regex="password|refresh_token"),
        username: str = Form(default=""),
        password: str = Form(default=""),
        refresh_token: str = Form(default=""),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ) -> None:
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.scopes = scope.split()
        self.refresh_token = refresh_token


def authenticate_user_password(
    username: str,
    password: str,
    db: Session = Depends(get_session),
) -> User:
    user = get_user(username, db=db)
    if not verify_password(password, user.hashed_password):
        raise UsernameOrPasswordIncorrectError
    return user


def authenticate_user_token(
    token: str,
    db: Session = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(
            token,
            auth_settings.SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )
        email = payload.get("sub")
        if email is None:
            raise CredentialsIncorrectError
    except JWTError as e:
        raise CredentialsIncorrectError from e
    return get_user(email=email, db=db)


def create_token(
    data: dict[str, Any],
    expires_delta: timedelta,
    algorithm: str = auth_settings.ALGORITHM,
) -> str:
    to_encode = data.copy()
    expire = get_now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        auth_settings.SECRET_KEY,
        algorithm=algorithm,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    return authenticate_user_token(token, db=db)


def create_tokens_from_user(user: User) -> dict[str, str]:
    jwt_data = {"sub": str(user.email)}

    access_token = create_token(
        data=jwt_data,
        expires_delta=timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        data=jwt_data,
        expires_delta=timedelta(minutes=auth_settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from api.config import get_auth_settings
from api.database import get_session
from api.public.auth.crud import get_user
from api.public.auth.helpers import verify_password
from api.public.auth.models import User
from api.utils.exceptions import (
    CredentialsIncorrectError,
    EmailOrPasswordIncorrectError,
)
from api.utils.helpers import get_now

auth_settings = get_auth_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def authenticate_user_password(
    username: str,
    password: str,
    db: Session = Depends(get_session),
) -> User:
    user = get_user(username, db=db)
    if not verify_password(password, user.hashed_password):
        raise EmailOrPasswordIncorrectError
    return user


def authenticate_user_token(
    token: str,
    db: Session = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(
            jwt=token,
            key=auth_settings.TERASTORE_JWT_SECRET,
            algorithms=[auth_settings.ALGORITHM],
        )
        email = payload.get("sub")
        if email is None:
            raise CredentialsIncorrectError
    except jwt.DecodeError as e:
        raise CredentialsIncorrectError from e
    return get_user(email=email, db=db)


def create_token(
    data: dict[str, Any],
    expires: datetime,
    algorithm: str = auth_settings.ALGORITHM,
) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": expires})
    return jwt.encode(
        payload=to_encode, key=auth_settings.TERASTORE_JWT_SECRET, algorithm=algorithm
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    return authenticate_user_token(token, db=db)


def create_tokens_from_user(response: Response, user: User) -> str:
    jwt_data = {"sub": str(user.email), "auth_level": user.auth_level.value}

    access_token_expires = get_now() + timedelta(
        minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    access_token = create_token(
        data=jwt_data,
        expires=access_token_expires,
    )

    refresh_token_expires = get_now() + timedelta(
        minutes=auth_settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_token(
        data=jwt_data,
        expires=refresh_token_expires,
    )

    response.set_cookie(
        key=auth_settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        expires=int(refresh_token_expires.timestamp()),
        httponly=True,
    )
    return access_token


def logout_user(response: Response) -> Response:
    response.delete_cookie(
        key=auth_settings.REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
    )
    return response

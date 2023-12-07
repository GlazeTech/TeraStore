from datetime import timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session

from api.config import get_auth_settings
from api.database import get_session
from api.public.auth.crud import get_user
from api.public.auth.helpers import verify_password
from api.public.auth.models import TokenData, User
from api.utils.exceptions import UsernameOrPasswordIncorrectError
from api.utils.helpers import get_now

auth_settings = get_auth_settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate_user(
    username: str,
    password: str,
    db: Session = Depends(get_session),
) -> User:
    user = get_user(username, db=db)
    if not verify_password(password, user.hashed_password):
        raise UsernameOrPasswordIncorrectError
    return user


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = get_now() + expires_delta
    else:
        expire = get_now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        auth_settings.SECRET_KEY,
        algorithm=auth_settings.ALGORITHM,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            auth_settings.SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        raise credentials_exception from e
    user = get_user(email=token_data.email, db=db)
    if user is None:
        raise credentials_exception
    return user

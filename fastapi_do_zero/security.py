from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
)
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_do_zero.database import start_database
from fastapi_do_zero.models import User
from fastapi_do_zero.settings import Settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
settings = Settings()


def get_pwd_hash(password):
    return pwd_context.hash(password)


def verify_pwd_hash(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def generate_token(data: dict):
    to_encode = data.copy()

    expires_in = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expires_in})

    encoded_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


async def get_current_user(
    session: AsyncSession = Depends(start_database),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload_jwt = decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        subject_email = payload_jwt.get("sub")

        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    db_user = await session.scalar(
        select(User).where(User.email == subject_email))

    if not db_user:
        raise credentials_exception

    return db_user

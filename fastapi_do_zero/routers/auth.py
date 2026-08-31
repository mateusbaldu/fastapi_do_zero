from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_do_zero.database import start_database
from fastapi_do_zero.models import User
from fastapi_do_zero.schema import (
    Token,
)
from fastapi_do_zero.security import (
    generate_token,
    verify_pwd_hash,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
Session = Annotated[Session, Depends(start_database)]
FormData = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/token", response_model=Token)
def login(session: Session, form_data: FormData):
    db_user = session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_pwd_hash(form_data.password, db_user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = generate_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "Bearer"}

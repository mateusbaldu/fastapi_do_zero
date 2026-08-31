from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_do_zero.database import start_database
from fastapi_do_zero.models import User
from fastapi_do_zero.schema import (
    FilterPage,
    ListUser,
    UserResponseSchema,
    UserSchema,
)
from fastapi_do_zero.security import (
    get_current_user,
    get_pwd_hash,
)

router = APIRouter(prefix="/users", tags=["users"])
Session = Annotated[AsyncSession, Depends(start_database)]
CurrentUser = Annotated[User, Depends(get_current_user)]
QueryFilterPage = Annotated[FilterPage, Query()]


@router.post("/", status_code=201, response_model=UserResponseSchema)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"User {user.username} or email {user.email} already taken",
        )

    db_user = User(
        username=user.username,
        password=get_pwd_hash(user.password),
        email=user.email,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get("/", status_code=200, response_model=ListUser)
async def fetch_all_users(session: Session, filter_users: QueryFilterPage):
    users = await session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    )
    return {"users": users}


@router.put("/{user_id}", status_code=200, response_model=UserResponseSchema)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You dont have permission to perform this action",
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_pwd_hash(user.password)

        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"User {user.username} or email {user.email} already taken",
        )


@router.get("/{user_id}", status_code=200, response_model=UserResponseSchema)
async def fetch_user(user_id: int, session: Session):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )

    return db_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
        user_id: int,
        session: Session,
        current_user: CurrentUser
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You dont have permission to perform this action",
        )

    await session.delete(current_user)

from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette.responses import HTMLResponse

from fastapi_do_zero.database import start_database
from fastapi_do_zero.models import User
from fastapi_do_zero.schema import (
    ListUser,
    Message,
    UserResponseSchema,
    UserSchema,
)

app = FastAPI()


@app.get("/", status_code=200, response_model=Message)
def read_root():
    return {"message": "Hello World"}


@app.get("/olamundo", status_code=200, response_class=HTMLResponse)
def ola_mundo():
    return """
    <html>
        <head><title>Titulo</title></head>
        <body><h1>Ola Mundo</h1></body>
    <html>
    """


@app.post("/users", status_code=201, response_model=UserResponseSchema)
def create_user(user: UserSchema, session=Depends(start_database)):
    db_user = session.scalar(
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
        username=user.username, password=user.password, email=user.email
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    session.close()

    return db_user


@app.get("/users", status_code=200, response_model=ListUser)
def fetch_all_users(limit=10, offset=0, session=Depends(start_database)):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {"users": users}


@app.put(
    "/users/{user_id}", status_code=200, response_model=UserResponseSchema
)
def update_user(
    user_id: int, user: UserSchema, session=Depends(start_database)
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )

    try:
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = user.password

        session.commit()
        session.refresh(db_user)

        return db_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"User {user.username} or email {user.email} already taken",
        )


@app.get(
    "/users/{user_id}", status_code=200, response_model=UserResponseSchema
)
def fetch_user(user_id: int, session=Depends(start_database)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )

    return db_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, session=Depends(start_database)):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )

    session.delete(db_user)

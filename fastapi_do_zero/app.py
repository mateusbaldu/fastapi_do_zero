from fastapi import FastAPI, HTTPException
from starlette.responses import HTMLResponse

from fastapi_do_zero.schema import (
    ListUser,
    Message,
    UserDB,
    UserResponseSchema,
    UserSchema,
)

app = FastAPI()

database = []


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
def create_user(user: UserSchema):
    user_with_id = UserDB(
        **user.model_dump(),
        id=len(database) + 1,
    )
    database.append(user_with_id)
    return user_with_id


@app.get("/users", status_code=200, response_model=ListUser)
def fetch_all_users():
    return {"users": database}


@app.put(
    "/users/{user_id}", status_code=200, response_model=UserResponseSchema
)
def update_user(user_id: int, user: UserSchema):
    user_with_id = UserDB(
        **user.model_dump(),
        id=user_id,
    )
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )
    database[user_id - 1] = user_with_id
    return user_with_id


@app.get(
    "/users/{user_id}", status_code=200, response_model=UserResponseSchema
)
def fetch_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )
    return database[user_id - 1]


@app.delete(
    "/users/{user_id}", status_code=204
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            detail=f"User with id {user_id} does not exist",
            status_code=404,
        )

    database.pop(user_id - 1)

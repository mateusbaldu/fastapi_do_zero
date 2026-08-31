from fastapi import FastAPI
from starlette.responses import HTMLResponse

from fastapi_do_zero.routers import auth, users
from fastapi_do_zero.schema import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


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

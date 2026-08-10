from http import HTTPStatus


def test_root_deve_retornar_ola_mundo(client):
    """
    Triple AAA
    - Arrange - Preparo
    - Act - Executa (SUT)
    - Assert - Garante que A é A
    """
    # Arrange

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World"}


def test_ola_mundo_deve_retornar_ola_mundo(client):

    response = client.get("/olamundo")

    assert response.status_code == HTTPStatus.OK
    assert (
        response.text
        == """
    <html>
        <head><title>Titulo</title></head>
        <body><h1>Ola Mundo</h1></body>
    <html>
    """
    )


def test_create_user(client):

    response = client.post(
        "/users",
        json={
            "username": "Alice",
            "password": "alice",
            "email": "alice@email.com",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "email": "alice@email.com",
    }


def fetch_all_users(client):
    response = client.get("/users")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "id": 1,
                "username": "Alice",
                "email": "alice@email.com",
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        "/users/1",
        json={
            "username": "Bob",
            "email": "bob@email.com",
            "password": "secreto",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "Bob",
        "email": "bob@email.com",
        "id": 1
    }


def test_update_user_return_not_found(client):
    response = client.put(
        "/users/2",
        json={
            "username": "Bob",
            "email": "bob@email.com",
            "password": "secreto",
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User with id 2 does not exist"
    }


def delete_user(client):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.json() == {}


def test_delete_user_return_not_found(client):
    response = client.delete(
        "/users/2"
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User with id 2 does not exist"
    }


def test_fetch_user(client):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "Bob",
        "email": "bob@email.com",
        "id": 1
    }


def test_fetch_user_return_not_found(client):
    response = client.get("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {
        "detail": "User with id 2 does not exist"
    }

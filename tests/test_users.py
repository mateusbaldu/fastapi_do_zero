from http import HTTPStatus

from fastapi_do_zero.schema import UserResponseSchema


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


def test_create_user_return_conflict(client, mock_user):
    response = client.post(
        "/users",
        json={
            "username": mock_user.username,
            "email": mock_user.email,
            "password": mock_user.password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": f"User {mock_user.username} or email "
        f"{mock_user.email} already taken"
    }


def test_fetch_all_users(client, mock_user, token):
    user_schema = UserResponseSchema.model_validate(mock_user).model_dump()
    response = client.get(
        "/users", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_user(client, mock_user, token):
    response = client.put(
        f"/users/{mock_user.id}",
        json={
            "username": "Bob",
            "email": "bob@email.com",
            "password": "secreto",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "Bob",
        "email": "bob@email.com",
        "id": 1,
    }


def test_update_user_return_forbidden(
    client, mock_user, mock_other_user, token
):
    response = client.put(
        f"/users/{mock_other_user.id}",
        json={
            "username": "Bob",
            "email": "bob@email.com",
            "password": "secreto",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "detail": "You dont have permission to perform this action"
    }


def test_update_integrity_error(client, mock_user, mock_other_user, token):
    other_username = mock_other_user.username
    other_email = mock_other_user.email

    response = client.put(
        f"/users/{mock_user.id}",
        json={
            "username": other_username,
            "email": other_email,
            "password": mock_other_user.clean_pwd,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        "detail": f"User {other_username} "
                  f"or email {other_email} already taken"
    }


def test_delete_user(client, mock_user, token):
    response = client.delete(
        f"/users/{mock_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_return_forbidden(client, token):
    response = client.delete(
        "/users/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        "detail": "You dont have permission to perform this action"
    }


def test_fetch_user(client, mock_user):
    response = client.get("/users/1")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": mock_user.username,
        "email": mock_user.email,
        "id": mock_user.id,
    }


def test_fetch_user_return_not_found(client):
    response = client.get("/users/2")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User with id 2 does not exist"}

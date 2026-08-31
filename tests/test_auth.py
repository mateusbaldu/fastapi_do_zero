from http import HTTPStatus


def test_login(client, mock_user):
    response = client.post(
        "/auth/token",
        data={"username": mock_user.email, "password": mock_user.clean_pwd},
    )

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"


def test_login_user_not_found(client):
    response = client.post(
        "/auth/token",
        data={"username": "test", "password": "abc123"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}


def test_login_wrong_pwd(client, mock_user):
    response = client.post(
        "/auth/token",
        data={"username": mock_user.email, "password": "wrongPassword"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}

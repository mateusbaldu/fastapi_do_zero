from http import HTTPStatus

from freezegun import freeze_time


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


def test_token_expired(client, mock_user):
    with freeze_time("2025-09-27 12:00:00"):
        response = client.post(
            "/auth/token",
            data={
                "username": mock_user.email,
                "password": mock_user.clean_pwd,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2025-09-27 13:00:00"):
        response = client.put(
            f"/users/{mock_user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
                "password": "wrong",
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


def test_refresh_token(client, mock_user, token):
    response = client.post(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_token_expired_dont_refresh(client, mock_user):
    with freeze_time("2023-07-14 12:00:00"):
        response = client.post(
            "/auth/token",
            data={
                "username": mock_user.email,
                "password": mock_user.clean_pwd,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2023-07-14 13:30:00"):
        response = client.post(
            "/auth/refresh_token",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}

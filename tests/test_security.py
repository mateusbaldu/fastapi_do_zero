from http import HTTPStatus

from jwt import decode

from fastapi_do_zero.security import generate_token


def test_generate_token(settings):
    claim = {"test": "test"}
    token = generate_token(claim)
    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded["test"] == claim["test"]
    assert "exp" in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        "/users/1",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_jwt_without_sub(client):
    data = {"no-email": "test"}
    fake_jwt = generate_token(data)
    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {fake_jwt}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_jwt_subject_dont_exists(client):
    data = {"sub": "test@email.com"}
    fake_jwt = generate_token(data)
    response = client.delete(
        "/users/1", headers={"Authorization": f"Bearer {fake_jwt}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}

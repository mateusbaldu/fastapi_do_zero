from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_do_zero.app import app


def test_root_deve_retornar_ola_mundo():
    """
    Triple AAA
    - Arrange - Preparo
    - Act - Executa (SUT)
    - Assert - Garante que A é A
    """
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World"}

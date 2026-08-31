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

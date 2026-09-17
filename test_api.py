import pytest
from unittest.mock import MagicMock, patch

from api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@patch("api.connect_db")
def test_lista_todos_os_imoveis(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.fetchall.return_value = [
        (
            1,
            "Nicole Common",
            "Travessa",
            "Lake Danielle",
            "Judymouth",
            "85184",
            "casa em condominio",
            488423.52,
            "2017-07-29",
        )
    ]

    # When
    response = client.get("/imoveis")

    # Then
    assert response.status_code == 200
    assert response.get_json() == {
        "imoveis": [
            {
                "id": 1,
                "logradouro": "Nicole Common",
                "tipo_logradouro": "Travessa",
                "bairro": "Lake Danielle",
                "cidade": "Judymouth",
                "cep": "85184",
                "tipo": "casa em condominio",
                "valor": 488423.52,
                "data_aquisicao": "2017-07-29",
            }
        ]
    }
    mock_cursor.execute.assert_called_once_with("SELECT * FROM imoveis")


@patch("api.connect_db")
def test_busca_imovel_por_id(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.fetchone.return_value = (
        1,
        "Nicole Common",
        "Travessa",
        "Lake Danielle",
        "Judymouth",
        "85184",
        "casa em condominio",
        488423.52,
        "2017-07-29",
    )

    # When
    response = client.get("/imoveis/1")

    # Then
    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "logradouro": "Nicole Common",
        "tipo_logradouro": "Travessa",
        "bairro": "Lake Danielle",
        "cidade": "Judymouth",
        "cep": "85184",
        "tipo": "casa em condominio",
        "valor": 488423.52,
        "data_aquisicao": "2017-07-29",
    }
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s", (1,)
    )


@patch("api.connect_db")
def test_busca_imovel_inexistente(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.fetchone.return_value = None

    # When
    response = client.get("/imoveis/9999")

    # Then
    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

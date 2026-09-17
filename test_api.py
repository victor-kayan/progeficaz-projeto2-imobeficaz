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


@patch("api.connect_db")
def test_adiciona_novo_imovel(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.lastrowid = 1001
    novo_imovel = {
        "logradouro": "Rua das Flores",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "cep": "01001-000",
        "tipo": "apartamento",
        "valor": 500000.0,
        "data_aquisicao": "2026-09-16",
    }

    # When
    response = client.post("/imoveis", json=novo_imovel)

    # Then
    assert response.status_code == 201
    assert response.get_json() == {
        "mensagem": "Imóvel criado com sucesso",
        "id": 1001,
    }
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO imoveis "
        "(logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, "
        "data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            "Rua das Flores",
            "Rua",
            "Centro",
            "São Paulo",
            "01001-000",
            "apartamento",
            500000.0,
            "2026-09-16",
        ),
    )
    mock_conn.commit.assert_called_once()


@pytest.mark.parametrize(
    "dados_incompletos",
    [
        {"cidade": "São Paulo"},
        {"logradouro": "Rua das Flores"},
    ],
)
@patch("api.connect_db")
def test_adiciona_imovel_sem_campos_obrigatorios(
    mock_connect_db, client, dados_incompletos
):
    # Given
    mensagem_esperada = {"erro": "Logradouro e cidade são obrigatórios"}

    # When
    response = client.post("/imoveis", json=dados_incompletos)

    # Then
    assert response.status_code == 400
    assert response.get_json() == mensagem_esperada
    mock_connect_db.assert_not_called()

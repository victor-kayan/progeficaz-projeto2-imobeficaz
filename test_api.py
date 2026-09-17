import pytest
from unittest.mock import MagicMock, patch

from api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_raiz_apresenta_links_da_api(client):
    # When
    response = client.get("/")

    # Then
    assert response.status_code == 200
    assert response.get_json() == {
        "nome": "ImobEficaz API",
        "_links": {
            "imoveis": {"href": "/imoveis", "method": "GET"},
            "criar_imovel": {"href": "/imoveis", "method": "POST"},
            "buscar_por_tipo": {
                "href": "/imoveis/tipo/{tipo}",
                "method": "GET",
                "templated": True,
            },
            "buscar_por_cidade": {
                "href": "/imoveis/cidade/{cidade}",
                "method": "GET",
                "templated": True,
            },
        },
    }


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
                "_links": {
                    "self": {"href": "/imoveis/1", "method": "GET"},
                    "colecao": {"href": "/imoveis", "method": "GET"},
                    "atualizar": {"href": "/imoveis/1", "method": "PUT"},
                    "remover": {"href": "/imoveis/1", "method": "DELETE"},
                },
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
        "_links": {
            "self": {"href": "/imoveis/1", "method": "GET"},
            "colecao": {"href": "/imoveis", "method": "GET"},
            "atualizar": {"href": "/imoveis/1", "method": "PUT"},
            "remover": {"href": "/imoveis/1", "method": "DELETE"},
        },
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
        "_links": {
            "self": {"href": "/imoveis/1001", "method": "GET"},
            "colecao": {"href": "/imoveis", "method": "GET"},
        },
    }
    assert response.headers["Location"] == "/imoveis/1001"
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


@patch("api.connect_db")
def test_atualiza_imovel(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.rowcount = 1
    dados_atualizados = {
        "logradouro": "Avenida Paulista",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 750000.0,
        "data_aquisicao": "2026-09-16",
    }

    # When
    response = client.put("/imoveis/1", json=dados_atualizados)

    # Then
    assert response.status_code == 200
    assert response.get_json() == {
        "mensagem": "Imóvel atualizado com sucesso",
        "_links": {
            "self": {"href": "/imoveis/1", "method": "GET"},
            "colecao": {"href": "/imoveis", "method": "GET"},
        },
    }
    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, "
        "bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, "
        "data_aquisicao = %s WHERE id = %s",
        (
            "Avenida Paulista",
            "Avenida",
            "Bela Vista",
            "São Paulo",
            "01310-100",
            "apartamento",
            750000.0,
            "2026-09-16",
            1,
        ),
    )
    mock_conn.commit.assert_called_once()


@patch("api.connect_db")
def test_atualiza_imovel_inexistente(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.rowcount = 0
    dados_atualizados = {
        "logradouro": "Avenida Paulista",
        "cidade": "São Paulo",
    }

    # When
    response = client.put("/imoveis/9999", json=dados_atualizados)

    # Then
    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@pytest.mark.parametrize(
    "dados_incompletos",
    [
        {"cidade": "São Paulo"},
        {"logradouro": "Avenida Paulista"},
    ],
)
@patch("api.connect_db")
def test_atualiza_imovel_sem_campos_obrigatorios(
    mock_connect_db, client, dados_incompletos
):
    # When
    response = client.put("/imoveis/1", json=dados_incompletos)

    # Then
    assert response.status_code == 400
    assert response.get_json() == {
        "erro": "Logradouro e cidade são obrigatórios"
    }
    mock_connect_db.assert_not_called()


@patch("api.connect_db")
def test_remove_imovel(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.rowcount = 1

    # When
    response = client.delete("/imoveis/1")

    # Then
    assert response.status_code == 204
    assert response.data == b""
    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = %s", (1,)
    )
    mock_conn.commit.assert_called_once()


@patch("api.connect_db")
def test_remove_imovel_inexistente(mock_connect_db, client):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.rowcount = 0

    # When
    response = client.delete("/imoveis/9999")

    # Then
    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}


@pytest.mark.parametrize(
    "rota, query, valor",
    [
        (
            "/imoveis/tipo/apartamento",
            "SELECT * FROM imoveis WHERE tipo = %s",
            "apartamento",
        ),
        (
            "/imoveis/cidade/São Paulo",
            "SELECT * FROM imoveis WHERE cidade = %s",
            "São Paulo",
        ),
    ],
)
@patch("api.connect_db")
def test_busca_imoveis_por_tipo_e_cidade(
    mock_connect_db, client, rota, query, valor
):
    # Given
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_db.return_value = mock_conn
    mock_cursor.fetchall.return_value = [
        (
            1,
            "Avenida Paulista",
            "Avenida",
            "Bela Vista",
            "São Paulo",
            "01310-100",
            "apartamento",
            750000.0,
            "2026-09-16",
        )
    ]

    # When
    response = client.get(rota)

    # Then
    assert response.status_code == 200
    assert response.get_json()["imoveis"][0]["id"] == 1
    assert response.get_json()["imoveis"][0]["tipo"] == "apartamento"
    assert response.get_json()["imoveis"][0]["cidade"] == "São Paulo"
    mock_cursor.execute.assert_called_once_with(query, (valor,))


@pytest.mark.parametrize(
    "metodo, rota",
    [
        ("POST", "/imoveis"),
        ("PUT", "/imoveis/1"),
    ],
)
@patch("api.connect_db")
def test_rejeita_corpo_json_nulo(mock_connect_db, client, metodo, rota):
    # When
    response = client.open(
        rota,
        method=metodo,
        data="null",
        content_type="application/json",
    )

    # Then
    assert response.status_code == 400
    assert response.get_json() == {
        "erro": "Logradouro e cidade são obrigatórios"
    }
    mock_connect_db.assert_not_called()

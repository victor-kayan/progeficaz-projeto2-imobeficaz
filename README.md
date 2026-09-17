# ImobEficaz

API RESTful de uma empresa imobiliária, desenvolvida para o Projeto 2 da disciplina de Programação Eficaz do Insper.

## Integrantes

- Victor Kayan
- Luigi Verdério

## Requisitos

- Python 3.11 ou superior
- MySQL hospedado no Aiven

## Configuração local

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

A aplicação utilizará as seguintes variáveis de ambiente para acessar o banco de dados:

```text
DB_HOST
DB_PORT
DB_USER
DB_PASSWORD
DB_NAME
```

As credenciais não devem ser adicionadas ao repositório.

No PowerShell, as variáveis podem ser definidas para a sessão atual com:

```powershell
$env:DB_HOST="host-do-aiven"
$env:DB_PORT="porta-do-aiven"
$env:DB_USER="usuario-do-aiven"
$env:DB_PASSWORD="senha-do-aiven"
$env:DB_NAME="nome-do-banco"
```

## Banco de dados

Crie um serviço MySQL no Aiven e conecte-o ao MySQL Workbench. Depois, execute o [script SQL oficial do projeto](https://insper.github.io/ProgramacaoEficaz/projetos/projeto2/imoveis.sql) para criar e preencher a tabela `imoveis`.

## Execução

Com o ambiente virtual ativo e as variáveis configuradas, execute:

```powershell
flask --app api run --debug
```

A API ficará disponível em `http://127.0.0.1:5000`.

## Rotas

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/` | Apresenta os links disponíveis na API |
| `GET` | `/imoveis` | Lista todos os imóveis |
| `GET` | `/imoveis/<id>` | Busca um imóvel pelo ID |
| `POST` | `/imoveis` | Adiciona um imóvel |
| `PUT` | `/imoveis/<id>` | Atualiza um imóvel |
| `DELETE` | `/imoveis/<id>` | Remove um imóvel |
| `GET` | `/imoveis/tipo/<tipo>` | Busca imóveis pelo tipo |
| `GET` | `/imoveis/cidade/<cidade>` | Busca imóveis pela cidade |

### Exemplo de criação

```json
{
  "logradouro": "Avenida Paulista",
  "tipo_logradouro": "Avenida",
  "bairro": "Bela Vista",
  "cidade": "São Paulo",
  "cep": "01310-100",
  "tipo": "apartamento",
  "valor": 750000.0,
  "data_aquisicao": "2026-09-16"
}
```

Os campos `logradouro` e `cidade` são obrigatórios. Os demais campos podem ser enviados como `null` ou omitidos.

## HATEOAS

A rota raiz informa como acessar a coleção, criar imóveis e realizar buscas. Cada imóvel retornado também contém controles hipermídia para consulta, atualização e remoção:

```json
{
  "_links": {
    "self": {"href": "/imoveis/1", "method": "GET"},
    "colecao": {"href": "/imoveis", "method": "GET"},
    "atualizar": {"href": "/imoveis/1", "method": "PUT"},
    "remover": {"href": "/imoveis/1", "method": "DELETE"}
  }
}
```

## Testes

Os testes automatizados serão executados com:

```powershell
pytest
```

Os testes utilizam o cliente de testes do Flask e mocks da conexão MySQL. Portanto, eles não modificam os dados hospedados no Aiven.

## Deploy

Em produção, a aplicação será executada com Gunicorn atrás do Nginx:

```bash
gunicorn --workers 3 --bind 127.0.0.1:5000 api:app
```

**URL pública:** será incluída após o deploy na AWS.

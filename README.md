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

O repositório contém modelos prontos para executar a aplicação com Gunicorn, `systemd` e Nginx. Os comandos abaixo consideram uma instância Ubuntu e o projeto em `/home/ubuntu/progeficaz-projeto2-imobeficaz`.

Instale os pacotes necessários e clone o repositório:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx ufw -y
git clone https://github.com/victor-kayan/progeficaz-projeto2-imobeficaz.git
cd progeficaz-projeto2-imobeficaz
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Crie `/etc/imobeficaz.env` no servidor, sem adicionar esse arquivo ao Git:

```bash
sudo nano /etc/imobeficaz.env
```

```text
DB_HOST="host-do-aiven"
DB_PORT="porta-do-aiven"
DB_USER="usuario-do-aiven"
DB_PASSWORD="senha-do-aiven"
DB_NAME="nome-do-banco"
```

Proteja as credenciais e instale o serviço:

```bash
sudo chown root:root /etc/imobeficaz.env
sudo chmod 600 /etc/imobeficaz.env
sudo cp deploy/imobeficaz.service /etc/systemd/system/imobeficaz.service
sudo systemctl daemon-reload
sudo systemctl enable --now imobeficaz
sudo systemctl status imobeficaz
```

Instale e valide a configuração do Nginx:

```bash
sudo cp deploy/nginx-imobeficaz.conf /etc/nginx/sites-available/imobeficaz
sudo ln -s /etc/nginx/sites-available/imobeficaz /etc/nginx/sites-enabled/imobeficaz
sudo unlink /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

No Security Group da EC2, permita SSH (`22`) apenas a partir do seu IP e HTTP (`80`) para os clientes da API. Depois, libere somente SSH e o Nginx no firewall da instância:

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
```

O Gunicorn escuta apenas em `127.0.0.1:5000`; a porta `5000` não precisa ser exposta publicamente. Verifique o serviço e a API com:

```bash
sudo journalctl -u imobeficaz --no-pager -n 50
curl http://127.0.0.1:5000/
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/imoveis
curl http://SEU_IP_PUBLICO/
```

**URL pública:** [http://54.172.144.227/](http://54.172.144.227/)

import os

import mysql.connector
from flask import Flask, jsonify, request


app = Flask(__name__)


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def formatar_imovel(registro):
    return {
        "id": registro[0],
        "logradouro": registro[1],
        "tipo_logradouro": registro[2],
        "bairro": registro[3],
        "cidade": registro[4],
        "cep": registro[5],
        "tipo": registro[6],
        "valor": registro[7],
        "data_aquisicao": registro[8],
    }


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis")
    registros = cursor.fetchall()

    imoveis = [formatar_imovel(registro) for registro in registros]

    cursor.close()
    conn.close()

    return jsonify({"imoveis": imoveis}), 200


@app.route("/imoveis", methods=["POST"])
def adicionar_imovel():
    dados = request.get_json()

    if not dados.get("logradouro") or not dados.get("cidade"):
        return jsonify({"erro": "Logradouro e cidade são obrigatórios"}), 400

    valores = (
        dados["logradouro"],
        dados.get("tipo_logradouro"),
        dados.get("bairro"),
        dados["cidade"],
        dados.get("cep"),
        dados.get("tipo"),
        dados.get("valor"),
        dados.get("data_aquisicao"),
    )

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imoveis "
        "(logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, "
        "data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        valores,
    )
    conn.commit()
    imovel_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({"mensagem": "Imóvel criado com sucesso", "id": imovel_id}), 201


@app.route("/imoveis/<int:imovel_id>", methods=["PUT"])
def atualizar_imovel(imovel_id):
    dados = request.get_json()
    valores = (
        dados["logradouro"],
        dados.get("tipo_logradouro"),
        dados.get("bairro"),
        dados["cidade"],
        dados.get("cep"),
        dados.get("tipo"),
        dados.get("valor"),
        dados.get("data_aquisicao"),
        imovel_id,
    )

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, "
        "bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, "
        "data_aquisicao = %s WHERE id = %s",
        valores,
    )
    conn.commit()
    imovel_atualizado = cursor.rowcount > 0

    cursor.close()
    conn.close()

    if not imovel_atualizado:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return jsonify({"mensagem": "Imóvel atualizado com sucesso"}), 200


@app.route("/imoveis/<int:imovel_id>", methods=["GET"])
def buscar_imovel(imovel_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (imovel_id,))
    registro = cursor.fetchone()

    cursor.close()
    conn.close()

    if registro is None:
        return jsonify({"erro": "Imóvel não encontrado"}), 404

    return jsonify(formatar_imovel(registro)), 200


if __name__ == "__main__":
    app.run(debug=True)

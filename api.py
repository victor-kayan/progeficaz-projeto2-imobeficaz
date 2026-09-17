import os

import mysql.connector
from flask import Flask, jsonify


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


@app.route("/imoveis/<int:imovel_id>", methods=["GET"])
def buscar_imovel(imovel_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis WHERE id = %s", (imovel_id,))
    registro = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(formatar_imovel(registro)), 200


if __name__ == "__main__":
    app.run(debug=True)

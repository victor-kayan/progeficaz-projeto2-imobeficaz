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


@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM imoveis")
    registros = cursor.fetchall()

    imoveis = []
    for registro in registros:
        imoveis.append(
            {
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
        )

    cursor.close()
    conn.close()

    return jsonify({"imoveis": imoveis}), 200


if __name__ == "__main__":
    app.run(debug=True)

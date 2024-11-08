from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import json
import hashlib
import psycopg2
from waitress import serve
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)  # Permitir CORS para todas las rutas y orígenes

app.config["JWT_SECRET_KEY"] = "super-secret"  # Cambia esto por una clave secreta más segura
jwt = JWTManager(app)



def load_file_config():
    with open('config.json') as f:
        return json.load(f)

data_config = load_file_config()
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=data_config['db']['database'],
            user=data_config['db']['user'],
            password=data_config['db']['password'],
            host=data_config['db']['host'],
            port=data_config['db']['port']
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


@app.route("/", methods=['GET'])
def test():
    return jsonify({"message": "Server running ..."}), 200


@app.route('/indicador_24', methods=['GET'])
def get_indicadores():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"msg": "Database connection error"}), 500

    cur = conn.cursor()

    try:
        cur.execute("""
             SELECT id, nombreindicador, areatematica, tema, desagregaciontematica,
                   clasificacion, "año", resultado, periodicidad, latitud,
                   longitud, departamento
            FROM indicadores.mercado_laboral_24_cauca
            WHERE resultado != 'ND' AND resultado != '' AND "año" = '2019'  ;
        """)
        indicadores = cur.fetchall()

        # Convertir los resultados a una lista de diccionarios
        result = []
        for indicador in indicadores:
            result.append({
                'id': indicador[0],
                'nombreindicador': indicador[1],
                'areatematica': indicador[2],
                'tema': indicador[3],
                'desagregaciontematica': indicador[4],
                'clasificacion': indicador[5],
                'año': indicador[6],
                'resultado': indicador[7],
                'periodicidad': indicador[8],
                'latitud': indicador[9],
                'longitud': indicador[10],
                'departamento': indicador[11]
            })
        return jsonify(result), 200
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return jsonify({"msg": "Database error"}), 500
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    print("Server running : " + "http://" + data_config["url-backend"] +
          ":" + str(data_config["port"]))
    serve(app, host=data_config["url-backend"], port=data_config["port"])

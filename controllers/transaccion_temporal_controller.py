from flask import Blueprint, request, jsonify
from models.transaccion_temporal_model import insert_transaccion_temporal, update_transaction_id

transactions_bp = Blueprint('transactions', __name__)

def registro_transaccion_temporal():
    try:
        data = request.json
        nombre = data.get("nombre")
        apellido = data.get("apellido")
        tipo_identificacion = data.get("tipo_identificacion")
        numero_identificacion = data.get("numero_identificacion")
        email = data.get("email")
        sexo = data.get("sexo")
        telefono = data.get("telefono")
        fecha_nacimiento = data.get("fecha_nacimiento")
        rol_id = data.get("rol_id")
        cantidad_licencia = data.get("cantidad_licencia")
        estado = data.get("estado")

        transaction_id = insert_transaccion_temporal(nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono,
                                     fecha_nacimiento, rol_id, cantidad_licencia, estado)

        return jsonify({"transaction_id": transaction_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def actualizar_transaction_id(id):
    data = request.get_json()
    transaction_id = data.get('transaction_id')

    if transaction_id is None:
        return jsonify({"error": "transaction_id es requerido"}), 400

    try:
        update_transaction_id(id, transaction_id)
        return jsonify({"message": "transaction_id actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


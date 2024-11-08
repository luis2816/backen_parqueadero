from flask import  jsonify

from models.webhook_model import get_webhook_id

def obtenerDetalleTransacción_id(id_transaccion):
    """Controlador para obtener un usuario por ID."""
    try:
        transaccion = get_webhook_id(id_transaccion)
        print(transaccion)
        if not transaccion:
            return jsonify({"msg": "Transacción not found"}), 404

        result = {
            'id': transaccion[0],
            'cantidad_licencia': transaccion[1],
            'valor_compra': transaccion[2],
            'fecha_registro': transaccion[3],
            'id_transaccion': transaccion[4],
            'estado': transaccion[5],
            'nombre': transaccion[6],
            'apellido': transaccion[7],
            'numero_identificacion': transaccion[8]
        }
        return jsonify(result), 200
    except Exception as e:
        print(e)
        return jsonify({"msg": str(e)}), 500

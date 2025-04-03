from flask import request, jsonify
from datetime import datetime

from models.movimiento_vehiculo import insert_movimiento_vehiculo, get_parking_status


def movimiento_vehiculo_controller():
    try:
        # Obtener datos del request
        data = request.get_json()

        # Validar campos obligatorios
        required_fields = ['placa', 'tipo', 'nombre', 'apartamento', 'parqueadero']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400

        # Procesar fecha_hora (usar la actual si no se proporciona)
        fecha_hora = data.get('fecha_hora', datetime.now())

        # Convertir string a datetime si es necesario
        if isinstance(fecha_hora, str):
            try:
                fecha_hora = datetime.fromisoformat(fecha_hora)
            except ValueError:
                return jsonify({"error": "Formato de fecha inválido. Usar ISO format (YYYY-MM-DD HH:MM:SS)"}), 400

        # Llamar al modelo
        movimiento_id = insert_movimiento_vehiculo(

            placa=data['placa'],
            fecha_hora=fecha_hora,
            tipo=data['tipo'],
            nombre=data['nombre'],
            apartamento=data['apartamento'],
            parqueadero=data['parqueadero'],
            id_residente=data.get('id_residente'),
            salida=data.get('salida')
        )

        return jsonify({
            "message": "Movimiento registrado exitosamente",
            "movimiento_id": movimiento_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_parking_detalle(id_conjunto):
    if not id_conjunto:
        return jsonify({"error": "id_conjunto is required"}), 400

    try:
        residentes = get_parking_status(id_conjunto)
        return jsonify({"status": 200, "data": residentes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

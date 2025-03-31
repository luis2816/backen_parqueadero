from flask import request, jsonify, current_app as app

from models.residentes_model import get_residentes_por_conjunto, insert_residente, insert_residente_conjunto
from models.vigilante_model import insert_vigilante, insert_vigilante_conjunto, \
    update_vigilante
import os
from models.user_model import update_user_photo, check_user_exists, get_user_id, update_user


def get_residentes():
    id_admin = request.args.get('id_admin')
    if not id_admin:
        return jsonify({"error": "id_admin is required"}), 400

    try:
        residentes = get_residentes_por_conjunto(id_admin)
        return jsonify({"status": 200, "data": residentes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def post_residente():
    print("ingreso aqui")

    data = request.json
    print(data)
    # Obtener y validar datos del cuerpo de la solicitud
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    tipo_identificacion = data.get('tipo_identificacion')
    numero_identificacion = data.get('numero_identificacion')
    email = data.get('email')
    sexo = data.get('sexo')
    telefono = data.get('telefono')
    fecha_nacimiento = data.get('fecha_nacimiento')
    tipo_vehiculo = data.get('tipo_vehiculo')
    placa = data.get('placa')
    marca = data.get('marca')
    color = data.get('color')
    modelo = data.get('modelo')
    numero_apartamento = data.get('numero_apartamento')
    numero_parqueadero = data.get('numero_parqueadero')
    id_conjunto = data.get('id_conjunto')
    estado = True


    try:
        # Verificar si el usuario ya está registrado
        #user_check = check_user_exists (email, numero_identificacion)
        #if user_check == "email_exists":
        #   return jsonify({"msg": "El correo electrónico ya se encuentra en uso", "status": 401}), 200
        #if user_check == "identification_exists":
        #   return jsonify({"msg": "El número de identificación ya se encuentra en uso", "status": 401}), 200

        # Insertar el nuevo usuario en la base de datos
        user_id = insert_residente(nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono, fecha_nacimiento, estado)
        if user_id:
            #Registarr relacion de residente por conjunto
            insert_residente_conjunto(user_id, id_conjunto,numero_apartamento, numero_parqueadero, tipo_vehiculo, placa, marca, color, modelo, estado)
        return jsonify({"status": 200, "msg": "Registro exitoso"}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"msg": str(e), "status": 500}), 500
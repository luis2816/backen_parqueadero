from flask import request, jsonify, current_app as app

from models.residentes_model import get_residentes_por_conjunto, insert_residente, insert_residente_conjunto, \
    update_residente, update_residente_conjunto, registrar_ingreso_residente
import os
from models.user_model import  get_user_id


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

def update_residente_controller(user_id):
    data = request.json
    id_residente_conjunto = data.get('id_residente_conjunto')

    print(data)

    # Obtener y validar datos del cuerpo de la solicitud
    updates = {
        "nombre": data.get('nombre'),
        "apellido": data.get('apellido'),
        "tipo_identificacion": data.get('tipo_identificacion'),
        "numero_identificacion": data.get('numero_identificacion'),
        "email": data.get('email'),
        "sexo": data.get('sexo'),
        "telefono": data.get('telefono'),
        "fecha_nacimiento": data.get('fecha_nacimiento'),
        "estado": data.get('estado'),
    }

    updates_residente_conjunto = {
        "numero_apartamento": data.get('numero_apartamento'),
        "numero_parqueadero": data.get('numero_parqueadero'),
        "placa": data.get('placa'),
        "tipo_vehiculo": data.get('tipo_vehiculo'),
        "color": data.get('color'),
        "marca": data.get('marca'),
        "modelo": data.get('modelo'),
    }

    # Eliminar claves con valores None
    updates = {k: v for k, v in updates.items() if v is not None}
    updates_residente_conjunto = {k: v for k, v in updates_residente_conjunto.items() if v is not None}

    try:
        # Verificar si el usuario existe
        if not get_user_id(user_id):
            return jsonify({"msg": "Usuario no encontrado"}), 404

        print("Usuario encontrado:", user_id)

        # Verificar si hay datos para actualizar
        if not updates and not updates_residente_conjunto:
            return jsonify({"msg": "No se enviaron campos para actualizar", "status": 400}), 400

        # Actualizar el usuario si hay datos para ello
        if updates:
            update_residente(user_id, updates)  # ✅ Pasar el diccionario directamente

        # Actualizar residente_conjunto si hay datos y un ID válido
        if updates_residente_conjunto and id_residente_conjunto:
            update_residente_conjunto(id_residente_conjunto, updates_residente_conjunto)  # ✅ Pasar el diccionario directamente

        return jsonify({"msg": "Residente actualizado exitosamente", "status": 200}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"msg": str(e), "status": 500}), 500

def get_registrar_ingreso_residente(placa):
    if not placa:
        return jsonify({"error": "placa is required"}), 400

    try:
        residentes = registrar_ingreso_residente(placa)
        return jsonify({"status": 200, "data": residentes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

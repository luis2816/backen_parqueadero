# controllers/user_controller.py
from flask import request, jsonify, send_from_directory, current_app as app
from models.user_model import get_users, get_token_info, get_user_by_email, hash_password, get_user_id, get_user_photo,check_user_exists, insert_user, update_user_photo, update_user, get_user_password, update_user_password, validate_token_and_update_password,check_user_exists_email
from flask_jwt_extended import create_access_token
from datetime import datetime

import os


def get_users_controller():
    """Controlador para obtener todos los usuarios."""
    try:
        usuarios = get_users()
        base_url = request.host_url + 'api/usuario/'
        result = []
        for usuario in usuarios:
            foto_perfil_url = f'{base_url}{usuario[0]}/foto' if usuario[14] else ''
            result.append({
                'id': usuario[0],
                'nombre': usuario[1],
                'apellido': usuario[2],
                'tipo_identificacion': usuario[3],
                'numero_identificacion': usuario[4],
                'sexo': usuario[5],
                'email': usuario[6],
                'password': usuario[7],
                'telefono': usuario[8],
                'fecha_nacimiento': usuario[9],
                'fecha_registro': usuario[10],
                'rol_id': usuario[11],
                'estado': usuario[12],
                'cantidad_licencia': usuario[13],
                'foto_perfil': usuario[14] if usuario[14] else '',
                'foto_perfil_url': foto_perfil_url
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
def login_controller():
    """Controlador para el inicio de sesión del usuario."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")


    # Buscar usuario en la base de datos por email
    user = get_user_by_email(email)
    print(user[4])
    print(hash_password(password))
    if user and user[4] == hash_password(password):  # user[4] es el hash MD5 en la BD        access_token = create_access_token(identity=email)
        access_token = create_access_token(identity=email)
        base_url = request.host_url + 'api/usuario/'
        foto_perfil_url = f'{base_url}{user[0]}/foto' if user[3] else ''
        user_data = {
            "id": user[0],
            "nombre": user[1],
            "apellido": user[2],
            "foto_perfil": foto_perfil_url,
        }

        print(user_data)
        return jsonify({"access_token": access_token, "user": user_data, "status": 200}), 200
    else:
        return jsonify({"message": "Credenciales incorrectas", "status": 401}), 200
def get_user_id_controller():
    user_id = request.args.get('id_usuario', type=int)

    """Controlador para obtener un usuario por ID."""
    try:
        usuario = get_user_id(user_id)
        print(usuario)
        if not usuario:
            return jsonify({"msg": "User not found"}), 404

        base_url = request.host_url + 'api/usuario/'
        foto_perfil_url = f'{base_url}{usuario[0]}/foto' if usuario[13] else ''

        ##Administrador de conjunto cerrado
        if usuario[11] == 1:
            result = {
                'id': usuario[0],
                'nombre': usuario[1],
                'apellido': usuario[2],
                'tipo_identificacion': usuario[3],
                'numero_identificacion': usuario[4],
                'sexo': usuario[5],
                'email': usuario[6],
                'telefono': usuario[8],
                'fecha_nacimiento': usuario[9],
                'fecha_registro': usuario[10],
                'rol_id': usuario[11],
                'estado': usuario[12],
                'cantidad_licencia': usuario[13],
                'foto_perfil': usuario[14] if usuario[14] else '',
                'foto_perfil_url': foto_perfil_url,
                'rol': usuario[15]
            }



        return jsonify(result), 200
    except Exception as e:
        print(e)
        return jsonify({"msg": str(e)}), 500
def get_user_photo_controller(user_id):
    """Controlador para obtener la foto de perfil de un usuario."""
    try:
        foto_perfil = get_user_photo(user_id)
        if not foto_perfil:
            return jsonify({"msg": "Usuario no encontrado o no tiene foto de perfil"}), 404

        return send_from_directory(app.config['UPLOAD_FOLDER_FOTO_PERFIL'], foto_perfil)
    except Exception as e:
        return jsonify({"msg": str(e)}), 500
def allowed_file(filename):
    # Define qué extensiones de archivo son permitidas
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def signup_controller():
    # Inicializar variables para el archivo
    filename = None
    file_path = None

    # Verificar si el archivo está en la solicitud
    if 'file' in request.files:
        file = request.files['file']

        # Verificar el archivo y prepararlo para guardarlo
        if file and allowed_file(file.filename):
            filename = "temp_foto" + os.path.splitext(file.filename)[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER_FOTO_PERFIL'], filename)

            try:
                file.save(file_path)
            except Exception as e:
                return jsonify({'msg': 'Error saving file', 'error': str(e)}), 500
        else:
            return jsonify({'msg': 'Tipo de imagen no permitido'}), 400

    # Obtener y validar datos del cuerpo de la solicitud
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    tipo_identificacion = request.form.get('tipo_identificacion')
    numero_identificacion = request.form.get('numero_identificacion')
    email = request.form.get('email')
    password = request.form.get('password')
    sexo = request.form.get('sexo')
    telefono = request.form.get('telefono')
    fecha_nacimiento = request.form.get('fecha_nacimiento')
    rol_id = request.form.get('rol_id')
    cantidad_licencia = request.form.get('cantidad_licencia')
    estado = request.form.get('estado')


    try:
        # Verificar si el usuario ya está registrado
        user_check = check_user_exists(email, numero_identificacion)
        if user_check == "email_exists":
            return jsonify({"msg": "El correo electrónico ya se encuentra en uso", "status": 401}), 200
        if user_check == "identification_exists":
            return jsonify({"msg": "El número de identificación ya se encuentra en uso", "status": 401}), 200

        # Insertar el nuevo usuario en la base de datos
        user_id = insert_user(nombre, apellido, tipo_identificacion, numero_identificacion, email, password, sexo, telefono, fecha_nacimiento, rol_id, cantidad_licencia, estado)

        # Si se proporcionó un archivo, renombrar el archivo con el ID de usuario real
        if filename and file_path:
            new_filename = f"{user_id}_foto{os.path.splitext(filename)[1]}"
            new_file_path = os.path.join(app.config['UPLOAD_FOLDER_FOTO_PERFIL'], new_filename)

            try:
                os.rename(file_path, new_file_path)
            except Exception as e:
                return jsonify({'msg': 'Error renaming file', 'error': str(e)}), 500

            # Actualizar el nombre del archivo en la base de datos
            update_user_photo(user_id, new_filename)

        return jsonify({"status": 200, "msg": "Registro exitoso",  "id_usuario": user_id}), 200
    except Exception as e:
        return jsonify({"msg": str(e), "status": 500}), 500

def update_user_controller(user_id):
    # Verificar si el archivo está en la solicitud
    file = request.files.get('file')
    filename = None

    if file and file.filename:
        new_filename = f"{user_id}_foto{os.path.splitext(file.filename)[1]}"

        if allowed_file(new_filename):
            # Crear el nuevo nombre del archivo usando el user_id
            file_path = os.path.join(app.config['UPLOAD_FOLDER_FOTO_PERFIL'], new_filename)

            # Verificar si ya existe una foto para este usuario y eliminarla
            existing_file_path = os.path.join(app.config['UPLOAD_FOLDER_FOTO_PERFIL'], f"{user_id}_foto{os.path.splitext(file.filename)[1]}")
            if os.path.exists(existing_file_path):
                try:
                    os.remove(existing_file_path)
                except Exception as e:
                    return jsonify({'msg': 'Error removing existing file', 'error': str(e)}), 500

            try:
                file.save(file_path)
            except Exception as e:
                return jsonify({'msg': 'Error saving file', 'error': str(e)}), 500

            filename = new_filename

    # Obtener y validar datos del cuerpo de la solicitud
    updates = {
        "nombre": request.form.get('nombre'),
        "apellido": request.form.get('apellido'),
        "tipo_identificacion": request.form.get('tipo_identificacion'),
        "numero_identificacion": request.form.get('numero_identificacion'),
        "email": request.form.get('email'),
        "sexo": request.form.get('sexo'),
        "telefono": request.form.get('telefono'),
        "fecha_nacimiento": request.form.get('fecha_nacimiento'),
        "rol_id": request.form.get('rol_id'),
        "estado": request.form.get('estado'),
        "foto_perfil": filename
    }
    # Eliminar claves con valores None
    updates = {k: v for k, v in updates.items() if v is not None}

    try:
        # Verificar si el usuario existe
        if not get_user_id(user_id):
            return jsonify({"msg": "Usuario no encontrado"}), 404

        # Actualizar el usuario
        if updates:
            update_user(user_id, updates)
            return jsonify({"msg": "Usuario actualizado exitosamente", "status": 200}), 200
        else:
            return jsonify({"msg": "No se enviaron campos para actualizar", "status": 400}), 400
    except Exception as e:
        return jsonify({"msg": str(e), "status": 500}), 500
def cambiar_password(user_id):
    # Obtener y validar los datos de la solicitud
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"msg": "Faltan datos requeridos", "status": 400}), 400

    try:
        # Obtener la contraseña actual del usuario
        hashed_password_db = get_user_password(user_id)
        if hashed_password_db is None:
            return jsonify({"msg": "Usuario no encontrado", "status": 404}), 404

        # Verificar que la contraseña antigua sea correcta
        hashed_old_password = hash_password(old_password)
        if hashed_password_db != hashed_old_password:
            return jsonify({"msg": "La contraseña antigua es incorrecta", "status": 401}), 200

        # Hashear la nueva contraseña y actualizarla
        hashed_new_password = hash_password(new_password)
        update_user_password(user_id, hashed_new_password)

        return jsonify({"msg": "Contraseña actualizada exitosamente", "status": 200}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"msg": "Error interno", "status": 500}), 500

def reset_password():
    data = request.get_json()

    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({'message': 'Token and password are required'}), 400

    try:
        validate_token_and_update_password(token, new_password)
        return jsonify({'message': 'Password updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

def check_token(token):
    try:
        user_info = get_token_info(token)

        if not user_info:
            return jsonify({'valid': False, 'message': 'Token no encontrado o inválido'}), 404

        token_expiration, token_used = user_info

        if token_expiration < datetime.now():
            return jsonify({'valid': False, 'message': 'Token ha expirado'}), 400

        if token_used:
            return jsonify({'valid': False, 'message': 'El token ya ha sido utilizado'}), 400

        return jsonify({'valid': True, 'message': 'Token válido'}), 200

    except Exception as e:
        return jsonify({'message': f'Database error: {e}'}), 500


def verificar_user_email():
    try:
        data = request.get_json()
        print(data)
        # Validar que se envió el campo 'email'
        if not data or 'email' not in data:
            return jsonify({"msg": "Email es requerido", "status": 400}), 400

        email = data.get('email')

        # Verificar si el usuario ya está registrado por el email
        user_check = check_user_exists_email(email)
        if user_check == "email_exists":
            return jsonify({"msg": "El correo electrónico ya se encuentra en uso", "status": 401}), 200
        else:
            return jsonify({"msg": "El correo electrónico está disponible", "status": 200}), 200

    except Exception as e:
        return jsonify({"msg": str(e), "status": 500}), 500
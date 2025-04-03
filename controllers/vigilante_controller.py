from flask import request, jsonify, current_app as app
from models.vigilante_model import get_vigilantes_por_conjunto, insert_vigilante, insert_vigilante_conjunto, \
    update_vigilante
import os
from models.user_model import update_user_photo, check_user_exists, get_user_id


def get_vigilantes():
    id_admin = request.args.get('id_admin')
    if not id_admin:
        return jsonify({"error": "id_admin is required"}), 400

    try:
        vigilantes = get_vigilantes_por_conjunto(id_admin)
        return jsonify({"status": 200, "data": vigilantes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def allowed_file(filename):
    # Define qué extensiones de archivo son permitidas
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def post_vigilante():
    print("ingreso aqui")
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
                print()
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
    id_conjunto = request.form.get('id_conjunto')
    estado = True


    try:
        # Verificar si el usuario ya está registrado
        user_check = check_user_exists (email, numero_identificacion)
        if user_check == "email_exists":
           return jsonify({"msg": "El correo electrónico ya se encuentra en uso", "status": 401}), 200
        if user_check == "identification_exists":
           return jsonify({"msg": "El número de identificación ya se encuentra en uso", "status": 401}), 200

        # Insertar el nuevo usuario en la base de datos
        user_id = insert_vigilante(nombre, apellido, tipo_identificacion, numero_identificacion, email, password, sexo, telefono, fecha_nacimiento, rol_id, estado)
        if user_id:
            #Registarr relacion de vigilante por conjunto
            insert_vigilante_conjunto(user_id, id_conjunto)
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

        return jsonify({"status": 200, "msg": "Registro exitoso"}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"msg": str(e), "status": 500}), 500


def update_vigilante_controller(user_id):
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
        "estado": request.form.get('estado'),
        "foto_perfil": filename
    }
    # Eliminar claves con valores None
    updates = {k: v for k, v in updates.items() if v is not None}

    try:
        # Verificar si el usuario existe

        if not get_user_id(user_id):
            return jsonify({"msg": "Usuario no encontrado"}), 404

        print("para actualizar existe usuario")
        print(user_id)
        # Actualizar el usuario
        if updates:
            print("para actualizar")
            update_vigilante(user_id, updates)
            return jsonify({"msg": "Vigilante actualizado exitosamente", "status": 200}), 200
        else:
            return jsonify({"msg": "No se enviaron campos para actualizar", "status": 400}), 400
    except Exception as e:
        print(e)
        return jsonify({"msg": str(e), "status": 500}), 500
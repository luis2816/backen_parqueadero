from flask import request, jsonify, current_app as app
from models.vigilante_model import get_vigilantes_por_conjunto, insert_vigilante, insert_vigilante_conjunto
import os
from  models.user_model import update_user_photo


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
    id_conjunto = request.form.get('id_conjunto')
    estado = True


    try:
        # Verificar si el usuario ya está registrado
        #user_check = check_user_exists(email, numero_identificacion)
        #if user_check == "email_exists":
        #    return jsonify({"msg": "El correo electrónico ya se encuentra en uso", "status": 401}), 200
        #if user_check == "identification_exists":
        #    return jsonify({"msg": "El número de identificación ya se encuentra en uso", "status": 401}), 200

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


        return jsonify({"status": 200, "msg": "Registro exitoso",  "id_usuario": user_id}), 200
    except Exception as e:
        return jsonify({"msg": str(e), "status": 500}), 500

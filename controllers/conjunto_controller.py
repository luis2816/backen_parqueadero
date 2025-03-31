# controllers/conjunto_controller.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import request, jsonify, send_from_directory
from models.conjunto_model import insert_conjunto, update_conjunto, get_conjuntos_porUsuario, get_total_conjuntos_porUsuario
from datetime import datetime

UPLOAD_FOLDER = "Files/Modelos_3d"  # Ruta donde se guardarán los archivos
BASE_URL = "http://localhost:5000"  # Cambia esto en producción

# Crear la carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def insert_conjunto_controller():
    try:
        # Obtener datos del formulario
        data = request.form

        required_fields = [
            'nombre', 'direccion', 'telefono', 'numero_apartamentos',
            'numero_parqueaderos_residentes', 'numero_parqueaderos_visitantes',
            'usuario_id', 'descripcion', 'servicios_comunes', 'reglamento_interno',
            'email_contacto', 'website', 'departamento', 'municipio', 'codigo_postal'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"msg": f"Missing field: {field}", "status": 400}), 400

        # Extraer datos del formulario
        nombre = data.get('nombre')
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        numero_apartamentos = data.get('numero_apartamentos')
        numero_parqueaderos_residentes = data.get('numero_parqueaderos_residentes')
        numero_parqueaderos_visitantes = data.get('numero_parqueaderos_visitantes')
        usuario_id = data.get('usuario_id')
        descripcion = data.get('descripcion')
        servicios_comunes = data.get('servicios_comunes')
        reglamento_interno = data.get('reglamento_interno')
        email_contacto = data.get('email_contacto')
        website = data.get('website')
        departamento = data.get('departamento')
        municipio = data.get('municipio')
        codigo_postal = data.get('codigo_postal')

        # Manejo del archivo de soporte
        soporte_url = None
        if "soporte" in request.files:
            file = request.files["soporte"]
            if file and file.filename:
                # Obtener la extensión del archivo
                ext = file.filename.rsplit(".", 1)[-1].lower()

                # Generar un nombre único con UUID y timestamp
                unique_filename = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.{ext}"

                # Asegurar que la carpeta existe
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                file_path = os.path.join(UPLOAD_FOLDER, secure_filename(unique_filename))
                file.save(file_path)

                # Guardar solo la ruta relativa
                soporte_url = f"/uploads/modelos_3d/{unique_filename}"

        # Insertar en la base de datos con la ruta única del archivo
        insert_conjunto(
            nombre, direccion, telefono, numero_apartamentos,
            numero_parqueaderos_residentes, numero_parqueaderos_visitantes, usuario_id,
            descripcion, servicios_comunes, reglamento_interno, email_contacto,
            website, departamento, municipio, codigo_postal, soporte_url
        )

        return jsonify({"msg": "Registro exitoso", "status": 200, "soporte_url": soporte_url}), 200

    except Exception as e:
        return jsonify({"msg": str(e), "status": 500}), 500
def update_conjunto_controller(conjunto_id):
    try:
        # Obtener datos del formulario y archivo si existe
        data = request.form
        file = request.files.get("soporte")

        required_fields = [
            'nombre', 'direccion', 'telefono', 'numero_apartamentos',
            'numero_parqueaderos_residentes', 'numero_parqueaderos_visitantes',
            'usuario_id', 'descripcion', 'servicios_comunes', 'reglamento_interno',
            'email_contacto', 'website', 'departamento', 'municipio', 'codigo_postal'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"msg": f"Missing field: {field}", "status": 400}), 400

        # Procesar archivo si se sube uno nuevo
        soporte_path = None
        if file:
            filename = secure_filename(file.filename)
            soporte_path = os.path.join(UPLOAD_FOLDER, filename)

            # Crear carpeta si no existe
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            # Guardar archivo
            file.save(soporte_path)

            # Guardar ruta relativa en la base de datos
            soporte_path = f"/uploads/modelos_3d/{filename}"

        # Llamar a la función para actualizar en la base de datos
        update_conjunto(
            conjunto_id,
            data['nombre'], data['direccion'], data['telefono'], data['numero_apartamentos'],
            data['numero_parqueaderos_residentes'], data['numero_parqueaderos_visitantes'], data['usuario_id'],
            data['descripcion'], data['servicios_comunes'], data['reglamento_interno'],
            data['email_contacto'], data['website'], data['departamento'], data['municipio'], data['codigo_postal'],
            soporte_path  # Incluir la ruta del archivo si se subió
        )

        return jsonify({"msg": "Actualización exitosa", "status": 200}), 200

    except Exception as e:
        return jsonify({"msg": str(e), "status": 500}), 500
def obtener_conjuntos(id_usuario):
    try:
        conjuntos = get_conjuntos_porUsuario(id_usuario)
        return jsonify(conjuntos), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
def total_conjuntos():
    # Obtener el ID de usuario desde los parámetros de la consulta
    id_usuario = request.args.get('id_usuario', type=int)

    # Validar el ID de usuario
    if id_usuario is None:
        return jsonify({'error': 'El ID de usuario es requerido.'}), 400

    try:
        # Llamar a la función para obtener el total de conjuntos
        total = get_total_conjuntos_porUsuario(id_usuario)

        # Retornar la respuesta en formato JSON
        return jsonify({'id_usuario': id_usuario, 'total_conjuntos': total}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
def uploaded_file(filename):
    return send_from_directory("Files/Modelos_3d", filename)
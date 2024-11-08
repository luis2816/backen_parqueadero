# controllers/conjunto_controller.py
from flask import request, jsonify
from models.conjunto_model import insert_conjunto, get_conjuntos_porUsuario, get_total_conjuntos_porUsuario


def insert_conjunto_controller():
    # Obtener y validar datos del cuerpo de la solicitud
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided", "status": 400}), 400

    required_fields = [
        'nombre', 'direccion', 'telefono', 'numero_apartamentos',
        'numero_parqueaderos_residentes', 'numero_parqueaderos_visitantes',
        'usuario_id', 'descripcion', 'servicios_comunes', 'reglamento_interno',
        'email_contacto', 'website', 'zona', 'ciudad', 'codigo_postal'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Missing field: {field}", "status": 400}), 400

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
    zona = data.get('zona')
    ciudad = data.get('ciudad')
    codigo_postal = data.get('codigo_postal')

    try:
        # Insertar el nuevo conjunto en la base de datos
        insert_conjunto(
            nombre, direccion, telefono, numero_apartamentos,
            numero_parqueaderos_residentes, numero_parqueaderos_visitantes, usuario_id,
            descripcion, servicios_comunes, reglamento_interno, email_contacto,
            website, zona, ciudad, codigo_postal
        )
        return jsonify({"msg": "Registro exitoso", "status": 200}), 200
    except Exception as e:
        # Capturar el error y devolver una respuesta adecuada
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

from db import get_db_connection
from datetime import datetime
import psycopg2

def get_residentes_por_conjunto(id_admin):
    """Obtiene todos los vigilantes de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
           	select
		cc.id as id_conjunto,
		u.id,
		u.nombre,
		u.apellido,
		u.numero_identificacion,
		u.tipo_identificacion,
		u.sexo,
		u.email,
		u.telefono,
		u.fecha_nacimiento,
		cc.nombre as nombre_conjunto,
		rc.numero_apartamento,
		rc.numero_parqueadero,
		rc.tipo_vehiculo,
		rc.placa,
		rc.modelo,
		rc.marca,
		rc.color,
		rc.id as id_residente_conjunto
	from
		public.residentes_conjunto rc 
	inner join public.conjuntos_cerrados cc on
		cc.id = rc.id_conjunto
	inner join public.usuarios u on
		u.id = rc.usuario_id
	where
		cc.usuario_id = %s
        """, (id_admin,))
        columns = [desc[0] for desc in cur.description]
        residentes = [dict(zip(columns, row)) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        residentes = []
    finally:
        cur.close()
        conn.close()

    return residentes



def insert_residente(nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono,
                fecha_nacimiento, estado):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        # Verificar si se proporcionó una contraseña

        cur.execute(
            """
            INSERT INTO usuarios (nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono, fecha_nacimiento, rol_id, estado, cantidad_licencia, foto_perfil, reset_token, token_expiration,token_used )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """,
            (nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono,
             fecha_nacimiento, 3, estado, None, None, None, None, False)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.Error as e:
        print(e)
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def insert_residente_conjunto(usuario_id, id_conjunto, numero_apartamento, numero_parqueadero=None,
                              tipo_vehiculo=None, placa=None, marca=None, color=None, modelo=None, estado=True):

    print("valor del conjunto")
    print(id_conjunto)
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO residentes_conjunto (usuario_id, id_conjunto, numero_apartamento, numero_parqueadero, 
                                                 tipo_vehiculo, placa, marca, color, modelo, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (usuario_id, id_conjunto, numero_apartamento, numero_parqueadero,
                 tipo_vehiculo, placa, marca, color, modelo, estado)
            )
            residente_id = cur.fetchone()[0]
            conn.commit()
            return residente_id
    except psycopg2.Error as e:
        conn.rollback()  # Evita transacciones incompletas
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()  # Cierra la conexión siempre


def update_residente_conjunto(residente_id, updates):
    if not updates:
        return 0  # No hay nada que actualizar

    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    try:
        with conn.cursor() as cur:
            # Construir la consulta dinámicamente con solo los campos a actualizar
            fields = [f"{key} = %s" for key in updates.keys()]
            values = list(updates.values())  # Extrae solo los valores del diccionario
            values.append(residente_id)  # Agrega el ID del residente al final

            query = f"""
                UPDATE residentes_conjunto
                SET {", ".join(fields)}
                WHERE id = %s
            """

            cur.execute(query, values)  # Ahora los valores son una lista plana, sin diccionario
            conn.commit()
            return cur.rowcount  # Número de filas afectadas
    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()
def update_residente(user_id, updates):
    if not updates:
        return 0  # No hay nada que actualizar

    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    try:
        with conn.cursor() as cur:
            # Construir la consulta dinámicamente con solo los campos a actualizar
            fields = [f"{key} = %s" for key in updates.keys()]
            values = list(updates.values())  # Extrae solo los valores del diccionario
            values.append(user_id)  # Agrega el user_id al final

            query = f"""
                UPDATE usuarios
                SET {", ".join(fields)}
                WHERE id = %s
            """

            cur.execute(query, values)  # Ahora los valores son una lista plana, sin diccionario
            conn.commit()
            return cur.rowcount  # Número de filas afectadas
    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()


def registrar_ingreso_residente(placa):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Error de conexión a la base de datos")

    cur = conn.cursor()
    try:
        # 1. Consultar residente
        cur.execute("""
        SELECT
            u.nombre,
            rc.numero_apartamento AS apartamento,
            rc.numero_parqueadero AS parqueadero,
            rc.usuario_id AS id_residente,
            rc.id_conjunto AS id_conjunto
        FROM residentes_conjunto rc
        INNER JOIN usuarios u ON u.id = rc.usuario_id
        WHERE rc.placa = %s
        """, (placa,))

        residente = cur.fetchone()
        if not residente:
            return None

        # Convertir a diccionario
        columns = [desc[0] for desc in cur.description]
        residente_data = dict(zip(columns, residente))

        # 2. Verificar movimientos pendientes
        cur.execute("""
        SELECT id, fecha_hora FROM movimientos_vehiculos
        WHERE placa = %s AND salida IS NULL
        ORDER BY fecha_hora DESC
        LIMIT 1
        """, (placa,))

        movimiento_existente = cur.fetchone()
        if movimiento_existente:
            return residente_data

        # 3. Registrar nuevo movimiento
        tipo_movimiento = "Residente"  # En minúsculas para coincidir con constraints
        fecha_hora = datetime.now()

        cur.execute("""
        INSERT INTO movimientos_vehiculos 
            (placa, fecha_hora, tipo, nombre, apartamento, parqueadero, id_residente, id_conjunto)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fecha_hora;
        """, (
            placa,
            fecha_hora,
            tipo_movimiento,
            residente_data['nombre'],
            residente_data['apartamento'],
            residente_data['parqueadero'],
            residente_data['id_residente'],
            residente_data['id_conjunto']
        ))

        nuevo_movimiento = cur.fetchone()
        conn.commit()
        return residente_data

    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def registrar_salida_residente(placa):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Error de conexión a la base de datos")

    cur = conn.cursor()
    try:
        # 1. Verificar movimiento pendiente
        cur.execute("""
        SELECT 
            mv.id,
            mv.fecha_hora,
            mv.nombre,
            mv.apartamento,
            mv.parqueadero,
            mv.id_residente,
            rc.placa
        FROM movimientos_vehiculos mv
        LEFT JOIN residentes_conjunto rc ON mv.placa = rc.placa
        WHERE mv.placa = %s AND mv.salida IS NULL
        ORDER BY mv.fecha_hora DESC
        LIMIT 1
        """, (placa,))

        movimiento = cur.fetchone()

        if movimiento:
            # 2. Actualizar salida
            fecha_salida = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:23]

            cur.execute("""
            UPDATE movimientos_vehiculos
            SET salida = %s
            WHERE id = %s
            RETURNING id;
            """, (fecha_salida, movimiento[0]))

            movimiento_id = cur.fetchone()[0]
            conn.commit()

            # 3. Preparar respuesta exitosa
            return {
                'status': True,
                'data': {
                    'movimiento_id': movimiento_id,
                    'placa': placa,
                    'fecha_ingreso': movimiento[1],
                    'fecha_salida': fecha_salida,
                    'residente': {
                        'nombre': movimiento[2],
                        'apartamento': movimiento[3],
                        'parqueadero': movimiento[4],
                        'id_residente': movimiento[5]
                    }
                },
                'message': 'Salida registrada exitosamente'
            }
        else:
            # 4. Verificar si es residente
            cur.execute("""
            SELECT 
                u.nombre,
                rc.numero_apartamento,
                rc.numero_parqueadero,
                rc.usuario_id
            FROM residentes_conjunto rc
            JOIN usuarios u ON rc.usuario_id = u.id
            WHERE rc.placa = %s
            """, (placa,))

            residente = cur.fetchone()

            if residente:
                return {
                    'status': False,
                    'data': {
                        'placa': placa,
                        'residente': {
                            'nombre': residente[0],
                            'apartamento': residente[1],
                            'parqueadero': residente[2],
                            'id_residente': residente[3]
                        }
                    },
                    'message': 'No se encontró ingreso pendiente para esta placa'
                }
            else:
                return {
                    'status': False,
                    'data': None,
                    'message': 'Placa no registrada como residente'
                }

    except Exception as e:
        conn.rollback()
        return {
            'status': False,
            'data': None,
            'message': f'Error al procesar salida: {str(e)}'
        }
    finally:
        cur.close()
        conn.close()
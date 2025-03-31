from db import get_db_connection
import psycopg2
import hashlib
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
		rc.color
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
        vigilantes = []
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

def update_residente(user_id, updates):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        update_fields = ", ".join(f"{key} = %s" for key in updates.keys())
        values = list(updates.values()) + [user_id]
        query = f"UPDATE usuarios SET {update_fields} WHERE id = %s;"
        cur.execute(query, values)
        conn.commit()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()





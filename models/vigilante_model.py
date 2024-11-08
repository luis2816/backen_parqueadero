from db import get_db_connection
import psycopg2
import hashlib
def get_vigilantes_por_conjunto(id_admin):
    """Obtiene todos los vigilantes de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
           SELECT cc.id as id_conjunto, u.id, u.nombre, u.apellido, u.numero_identificacion, u.tipo_identificacion, u.sexo, u.email, u.telefono, u.fecha_nacimiento, u.foto_perfil
           FROM public.vigilantes_conjunto x
           INNER JOIN public.conjuntos_cerrados cc ON cc.id = x.id_conjunto 
           INNER JOIN public.usuarios u ON u.id = x.id_usuario  
           WHERE cc.usuario_id = %s 
        """, (id_admin,))
        columns = [desc[0] for desc in cur.description]
        vigilantes = [dict(zip(columns, row)) for row in cur.fetchall()]
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        vigilantes = []
    finally:
        cur.close()
        conn.close()

    return vigilantes


def hash_password(password):
    """Hashea la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def insert_vigilante(nombre, apellido, tipo_identificacion, numero_identificacion, email, password, sexo, telefono,
                fecha_nacimiento, rol_id, estado):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        # Verificar si se proporcionó una contraseña
        if password:
            hashed_password = hash_password(password)
        else:
            hashed_password = None  # O maneja el caso de contraseña no proporcionada según tu lógica

        cur.execute(
            """
            INSERT INTO usuarios (nombre, apellido, tipo_identificacion, numero_identificacion, email, password, sexo, telefono, fecha_nacimiento, rol_id, estado, cantidad_licencia, foto_perfil, reset_token, token_expiration,token_used )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """,
            (nombre, apellido, tipo_identificacion, numero_identificacion, email, hashed_password, sexo, telefono,
             fecha_nacimiento, rol_id, estado, None, None, None, None, False)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()



def insert_vigilante_conjunto(id_vigilante, id_conjunto):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO vigilantes_conjunto (id_usuario, id_conjunto)
            VALUES (%s, %s) RETURNING id;
            """,
            (id_vigilante, id_conjunto)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()






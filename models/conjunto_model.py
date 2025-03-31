# models/conjunto_model.py
from db import get_db_connection
import psycopg2

def insert_conjunto(nombre, direccion, telefono, numero_apartamentos, numero_parqueaderos_residentes, numero_parqueaderos_visitantes, usuario_id,
                    descripcion, servicios_comunes, reglamento_interno, email_contacto, website, departamento, municipio, codigo_postal, soporte_path):
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection error")

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conjuntos_cerrados (nombre, direccion, telefono, numero_apartamentos, numero_parqueaderos_residentes, numero_parqueaderos_visitantes, usuario_id,
                    descripcion, servicios_comunes, reglamento_interno, email_contacto, website, departamento, municipio, codigo_postal, soporte_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (nombre, direccion, telefono, numero_apartamentos, numero_parqueaderos_residentes, numero_parqueaderos_visitantes, usuario_id,
                 descripcion, servicios_comunes, reglamento_interno, email_contacto, website, departamento, municipio, codigo_postal, soporte_path)
            )
            conn.commit()
            return "Registro exitoso"
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        if conn is not None:
            conn.close()



def update_conjunto(conjunto_id, nombre, direccion, telefono, numero_apartamentos,
                    numero_parqueaderos_residentes, numero_parqueaderos_visitantes, usuario_id,
                    descripcion, servicios_comunes, reglamento_interno, email_contacto, website,
                    departamento, municipio, codigo_postal,soporte_path):
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection error")

        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE conjuntos_cerrados
                SET nombre = %s, direccion = %s, telefono = %s, numero_apartamentos = %s, 
                    numero_parqueaderos_residentes = %s, numero_parqueaderos_visitantes = %s, usuario_id = %s,
                    descripcion = %s, servicios_comunes = %s, reglamento_interno = %s, email_contacto = %s, 
                    website = %s, departamento = %s, municipio = %s, codigo_postal = %s, soporte_path =  %s
                WHERE id = %s;
                """,
                (nombre, direccion, telefono, numero_apartamentos, numero_parqueaderos_residentes,
                 numero_parqueaderos_visitantes, usuario_id, descripcion, servicios_comunes, reglamento_interno,
                 email_contacto, website, departamento, municipio, codigo_postal,soporte_path, conjunto_id, )
            )
            conn.commit()
            return "Actualización exitosa"
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        if conn is not None:
            conn.close()


def get_conjuntos_porUsuario(id_usuario):
    """Obtiene todos los conjuntos por administrador de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, nombre, direccion, telefono, numero_apartamentos, numero_parqueaderos_residentes,
                   numero_parqueaderos_visitantes, fecha_creacion, usuario_id, descripcion, servicios_comunes,
                   reglamento_interno, email_contacto, website, departamento, municipio, codigo_postal, estado, soporte_path
            FROM public.conjuntos_cerrados
            WHERE usuario_id = %s;
        """, (id_usuario,))
        rows = cur.fetchall()

        # Obtener los nombres de las columnas
        column_names = [desc[0] for desc in cur.description]

        # Convertir las filas a una lista de diccionarios
        conjuntos = []
        for row in rows:
            conjunto = dict(zip(column_names, row))
            conjuntos.append(conjunto)
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conjuntos = []
    finally:
        cur.close()
        conn.close()

    return conjuntos


def get_total_conjuntos_porUsuario(id_usuario):
    """Obtiene el total de conjuntos por administrador de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM public.conjuntos_cerrados
            WHERE usuario_id = %s;
        """, (id_usuario,))
        total_conjuntos = cur.fetchone()[0]
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        total_conjuntos = 0
    finally:
        cur.close()
        conn.close()

    return total_conjuntos

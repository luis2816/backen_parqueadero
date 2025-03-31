# models/user_model.py
from flask import request
import hashlib
import secrets
from db import get_db_connection
from datetime import datetime, timedelta
from utils.email_utils import send_email_to_user
import psycopg2
from flask import current_app



def hash_password(password):
    """Hashea la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_users():
    """Obtiene todos los usuarios de la base de datos."""
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, nombre, apellido, tipo_identificacion, numero_identificacion, 
                   sexo, email, "password", telefono, fecha_nacimiento, fecha_registro, 
                   rol_id, estado, cantidad_licencia, foto_perfil
            FROM public.usuarios;
        """)
        usuarios = cur.fetchall()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        usuarios = []
    finally:
        cur.close()
        conn.close()

    return usuarios

def get_user_by_email(email):
    """Obtiene un usuario por email."""
    conn = get_db_connection()
    if conn is None:
        return None

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, nombre, apellido, foto_perfil, password
            FROM usuarios
            WHERE email = %s;
        """, (email,))  # ✅ Agregar la coma final para evitar errores

        user = cur.fetchone()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        user = None
    finally:
        cur.close()
        conn.close()

    return user

def get_user_id(user_id):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
           SELECT s.id, s.nombre, s.apellido, s.tipo_identificacion, s.numero_identificacion, 
                   s.sexo, s.email, s.reset_token, s.telefono, s.fecha_nacimiento, s.fecha_registro, 
                   s.rol_id, s.estado, s.cantidad_licencia, s.foto_perfil, r.nombre 
            FROM public.usuarios as s
            inner join roles r on r.id  = s.rol_id 
             WHERE s.id  = %s;
        """, (user_id,))
        usuario = cur.fetchone()
        return usuario
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()



def get_user_photo(user_id):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()

    try:
        cur.execute("SELECT foto_perfil FROM public.usuarios WHERE id = %s;", (user_id,))
        result = cur.fetchone()
        return result[0] if result else None
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def check_user_exists(email, numero_identificacion):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        # Verificar si el usuario ya está registrado con el email
        cur.execute("SELECT * FROM usuarios WHERE email = %s;", (email,))
        if cur.fetchone():
            return "email_exists"

        # Verificar si el usuario ya está registrado con el número de identificación
        cur.execute("SELECT * FROM usuarios WHERE numero_identificacion = %s;", (numero_identificacion,))
        if cur.fetchone():
            return "identification_exists"

        return None
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def check_user_exists_email(email):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        # Verificar si el usuario ya está registrado con el email
        cur.execute("SELECT * FROM usuarios WHERE email = %s;", (email,))
        if cur.fetchone():
            return "email_exists"

        return None
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

def generate_token():
    return secrets.token_urlsafe(64)

def insert_user(nombre, apellido, tipo_identificacion, numero_identificacion, email, password, sexo, telefono,
                fecha_nacimiento, rol_id, cantidad_licencia, estado):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        token = generate_token()
        token_expiration = datetime.now() + timedelta(hours=24)  # Token válido por 24 horas

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
             fecha_nacimiento, rol_id, estado, cantidad_licencia, None, token, token_expiration, False)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def validate_token_and_update_password(token, new_password):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        # Consulta para obtener el usuario y el estado del token
        cur.execute(
            "SELECT id, token_expiration, token_used FROM usuarios WHERE reset_token = %s", (token,)
        )
        user = cur.fetchone()

        # Verifica si el usuario existe
        if not user:
            print("No se encontró un usuario con ese token")
            raise Exception("Invalid or expired token")

        user_id, token_expiration, token_used = user  # Desempaquetar la tupla

        # Verifica si el token ha expirado
        if token_expiration < datetime.now():
            print("Token ha expirado")
            print(token_expiration)
            raise Exception("Invalid or expired token")

        # Verifica si el token ya ha sido utilizado
        if token_used:
            print("El token ya ha sido utilizado")
            raise Exception("El token ya ha sido utilizado")

        # Hashear la nueva contraseña
        hashed_password = hash_password(new_password)

        # Actualizar la contraseña y marcar el token como utilizado
        cur.execute(
            "UPDATE usuarios SET password = %s, reset_token = NULL, token_expiration = NULL, token_used = TRUE WHERE id = %s",
            (hashed_password, user_id)
        )
        conn.commit()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

def update_user_photo(user_id, filename):
    """Actualizar el nombre del archivo de la foto de perfil en la base de datos"""
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("UPDATE usuarios SET foto_perfil = %s WHERE id = %s;", (filename, user_id))
        conn.commit()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

def update_user_estado(user_id, estado):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("UPDATE usuarios SET estado = %s WHERE id = %s;", (estado, user_id))
        conn.commit()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def update_user_cantidad_licencias(user_id, cantidad):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        # Verificar si el user_id existe
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE id = %s", (user_id,))
        exists = cur.fetchone()[0] > 0

        if not exists:
            print(f"El user_id {user_id} no existe.")
            return

        # Crear la consulta SQL
        query = "UPDATE usuarios SET cantidad_licencia = COALESCE(cantidad_licencia, 0) + %s WHERE id = %s"

        # Actualizar la cantidad de licencias
        cur.execute(query, (cantidad, user_id))
        conn.commit()

    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def update_user(user_id, updates):
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

def get_user_password(user_id):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM usuarios WHERE id = %s;", (user_id,))
            result = cur.fetchone()
            if result is None:
                return None
            return result[0]
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()

def update_user_password(user_id, new_password):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET password = %s WHERE id = %s;", (new_password, user_id))
            conn.commit()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()

def get_token_info(token):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT token_expiration, token_used FROM usuarios WHERE reset_token = %s", (token,)
        )
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()
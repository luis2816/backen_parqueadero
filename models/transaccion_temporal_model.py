from db import get_db_connection
import psycopg2
import hashlib
from datetime import datetime, timedelta


def insert_transaccion_temporal(nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono,
                fecha_nacimiento, rol_id, cantidad_licencia, estado):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:

        cur.execute("""
            INSERT INTO transacciones_temporales (nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo, telefono, fecha_nacimiento, rol_id, estado, cantidad_licencia, payment_status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """,
                    (nombre, apellido, tipo_identificacion, numero_identificacion, email, sexo,
                     telefono,
                     fecha_nacimiento, rol_id, estado, cantidad_licencia, 'pending', datetime.now())
                    )

        user_id = cur.fetchone()[0]
        conn.commit()

        return user_id
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def update_transaction_id(user_id, transaction_id):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE transacciones_temporales 
            SET transaction_id = %s
            WHERE id = %s;
        """, (transaction_id, user_id))

        conn.commit()
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def get_transaccion_temporal_byf_id(transaction_id):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, nombre, apellido, tipo_identificacion, numero_identificacion, sexo, email, telefono, 
                   fecha_nacimiento, rol_id, estado, cantidad_licencia, transaction_id, payment_status, created_at 
            FROM transacciones_temporales 
            WHERE id = %s;
        """, (transaction_id,))

        result = cur.fetchone()  # Obtener un único registro

        if result is None:
            return None  # Si no se encuentra, devuelve None

        # Convertir el resultado a un diccionario
        transaccion_temporal = {
            "id": result[0],
            "nombre": result[1],
            "apellido": result[2],
            "tipo_identificacion": result[3],
            "numero_identificacion": result[4],
            "sexo": result[5],
            "email": result[6],
            "telefono": result[7],
            "fecha_nacimiento": result[8],
            "rol_id": result[9],
            "estado": result[10],
            "cantidad_licencia": result[11],
            "transaction_id": result[12],
            "payment_status": result[13],
            "created_at": result[14]
        }

        return transaccion_temporal  # Devuelve el diccionario con los datos

    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

def delete_transaccion_temporal(user_id):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM transacciones_temporales 
            WHERE id = %s;
        """, (user_id,))

        # Verificamos cuántas filas se han borrado
        if cur.rowcount == 0:
            return False  # Si no se borró ninguna fila, devuelve False

        conn.commit()
        return True  # Si se borró correctamente, devuelve True
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

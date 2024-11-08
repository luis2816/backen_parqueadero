from db import get_db_connection
import psycopg2
import json
def insert_webhook(detalle, cantidad, valor_compra, id_usuario, id_transaccion, estado):
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection error")

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO webhook (detalle_transaccion, cantidad_licencia, valor_compra, id_usuario, id_transaccion, estado)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (json.dumps(detalle), cantidad, valor_compra, id_usuario, id_transaccion, estado)
            )
            conn.commit()
            return "Registro exitoso"
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        if conn is not None:
            conn.close()


def get_webhook_id(id_transaccion):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT w.id, w.cantidad_licencia, w.valor_compra, w.fecha_registro, w.id_transaccion, w.estado, u.nombre, u.apellido, u.numero_identificacion
            FROM public.webhook w
            INNER JOIN public.usuarios u ON u.id = w.id_usuario
            WHERE w.id_transaccion  = %s;
        """, (id_transaccion,))
        transaccion = cur.fetchone()

        return transaccion
    except psycopg2.Error as e:
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()

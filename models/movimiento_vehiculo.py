from db import get_db_connection
import psycopg2

def insert_movimiento_vehiculo(placa, fecha_hora, tipo, nombre, apartamento, parqueadero, id_residente=None, salida=None):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection error")

    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO movimientos_vehiculos 
            (placa, fecha_hora, tipo, salida, nombre, apartamento, parqueadero, id_residente)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """,
            (placa, fecha_hora, tipo, salida, nombre, apartamento, parqueadero, id_residente)
        )
        movimiento_id = cur.fetchone()[0]
        conn.commit()
        return movimiento_id
    except psycopg2.Error as e:
        print(e)
        raise Exception(f"Database error: {e}")
    finally:
        cur.close()
        conn.close()


def get_parking_status(id_conjunto: int) -> dict:
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la base de datos")

        cur = conn.cursor()

        # 1. Obtener metadata del conjunto
        cur.execute(
            "SELECT id, nombre, numero_parqueaderos_residentes FROM conjuntos_cerrados WHERE id = %s",
            (id_conjunto,)
        )
        if not (conjunto := cur.fetchone()):
            return {"success": False, "error": "Conjunto no encontrado"}

        id_conjunto, nombre_conjunto, total_spaces = conjunto

        # 2. Consulta 1: Vehículos actualmente estacionados (sin salida)
        cur.execute(
            """SELECT parqueadero, placa, apartamento, fecha_hora, nombre 
               FROM movimientos_vehiculos 
               WHERE id_conjunto = %s AND salida IS NULL""",
            (id_conjunto,)
        )
        ocupados_actuales = {int(row[0]): dict(zip(['parqueadero', 'placa', 'apartamento', 'fecha_hora', 'nombre'], row)) for row in cur.fetchall()}

        # 3. Consulta 2: Historial completo (todos los movimientos)
        cur.execute(
            """SELECT parqueadero, placa, apartamento, fecha_hora, salida, nombre 
               FROM movimientos_vehiculos 
               WHERE id_conjunto = %s
               ORDER BY fecha_hora DESC""",
            (id_conjunto,)
        )
        # Procesar todos los registros, no solo el más reciente
        historial_completo = []
        for row in cur.fetchall():
            historial_completo.append({
                "parqueadero": int(row[0]),
                "placa": row[1],
                "apartamento": row[2],
                "fecha_hora": row[3].isoformat() if row[3] else None,
                "salida": row[4].isoformat() if row[4] else None,
                "nombre": row[5]
            })

        # 4. Construir respuesta completa
        parking_spaces = []
        for space_num in range(1, total_spaces + 1):
            if space_num in ocupados_actuales:
                parking_spaces.append({
                    "id": space_num,
                    "status": "occupied",
                    "apartmentNumber": ocupados_actuales[space_num]["apartamento"],
                    "licensePlate": ocupados_actuales[space_num]["placa"]
                })
            else:
                parking_spaces.append({
                    "id": space_num,
                    "status": "available",
                    "apartmentNumber": None,
                    "licensePlate": None
                })

        return {
            "success": True,
            "totalSpaces": total_spaces,
            "parkingSpaces": parking_spaces,
            "ocupados_actuales": ocupados_actuales,
            "detalle": historial_completo,
            "conjunto": {
                "id": id_conjunto,
                "nombre": nombre_conjunto,
                "total_parqueaderos": total_spaces
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
    finally:
        if cur: cur.close()
        if conn: conn.close()
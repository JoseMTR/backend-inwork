from app.core.database import Database
from app.models.trabajo import Trabajo


class TrabajoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trabajos WHERE estado = TRUE ORDER BY created DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_trabajo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trabajos WHERE id_trabajo = %s AND estado = TRUE;", (id_trabajo,))
            return cursor.fetchone()
        finally:
            conn.close()

    def buscar_cercanos(self, latitud: float, longitud: float, radio_km: float):
        """Trabajos publicados a menos de radio_km (formula de Haversine)."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT * FROM (
                    SELECT t.*,
                           ROUND((6371 * 2 * ASIN(SQRT(
                               POWER(SIN(RADIANS(t.latitud - %s) / 2), 2) +
                               COS(RADIANS(%s)) * COS(RADIANS(t.latitud)) *
                               POWER(SIN(RADIANS(t.longitud - %s) / 2), 2)
                           )))::numeric, 2) AS distancia_km
                    FROM trabajos t
                    WHERE t.estado = TRUE AND t.estado_trabajo = 'publicado'
                ) cercanos
                WHERE distancia_km <= %s
                ORDER BY distancia_km;
            """
            cursor.execute(query, (latitud, latitud, longitud, radio_km))
            return cursor.fetchall()
        finally:
            conn.close()

    def crear(self, trabajo: Trabajo, id_cliente: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO trabajos (id_cliente, id_categoria, id_ciudad, titulo, descripcion, direccion,
                                      latitud, longitud, fecha_trabajo, hora_inicio, hora_fin,
                                      presupuesto, moneda)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_trabajo;
            """
            cursor.execute(query, (
                id_cliente, trabajo.id_categoria, trabajo.id_ciudad, trabajo.titulo, trabajo.descripcion,
                trabajo.direccion, trabajo.latitud, trabajo.longitud, trabajo.fecha_trabajo,
                trabajo.hora_inicio, trabajo.hora_fin, trabajo.presupuesto, trabajo.moneda
            ))
            nuevo_id = cursor.fetchone()["id_trabajo"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_trabajo: int, trabajo: Trabajo):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE trabajos
                SET id_categoria = %s, id_ciudad = %s, titulo = %s, descripcion = %s, direccion = %s,
                    latitud = %s, longitud = %s, fecha_trabajo = %s, hora_inicio = %s, hora_fin = %s,
                    presupuesto = %s, moneda = %s
                WHERE id_trabajo = %s AND estado = TRUE
                RETURNING id_trabajo;
            """
            cursor.execute(query, (
                trabajo.id_categoria, trabajo.id_ciudad, trabajo.titulo, trabajo.descripcion,
                trabajo.direccion, trabajo.latitud, trabajo.longitud, trabajo.fecha_trabajo,
                trabajo.hora_inicio, trabajo.hora_fin, trabajo.presupuesto, trabajo.moneda, id_trabajo
            ))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_trabajo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trabajos SET estado = FALSE WHERE id_trabajo = %s AND estado = TRUE RETURNING id_trabajo;",
                (id_trabajo,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

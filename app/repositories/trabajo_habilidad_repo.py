from app.core.database import Database
from app.models.trabajo_habilidad import TrabajoHabilidad


class TrabajoHabilidadRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trabajos_habilidades WHERE estado = TRUE ORDER BY id_trabajo_habilidad ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_trabajo(self, id_trabajo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT th.*, h.nombre AS habilidad
                FROM trabajos_habilidades th
                INNER JOIN habilidades h ON h.id_habilidad = th.id_habilidad
                WHERE th.id_trabajo = %s AND th.estado = TRUE;
            """
            cursor.execute(query, (id_trabajo,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_trabajo_habilidad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM trabajos_habilidades WHERE id_trabajo_habilidad = %s AND estado = TRUE;",
                (id_trabajo_habilidad,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, trabajo_habilidad: TrabajoHabilidad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO trabajos_habilidades (id_trabajo, id_habilidad)
                VALUES (%s, %s) RETURNING id_trabajo_habilidad;
            """
            cursor.execute(query, (trabajo_habilidad.id_trabajo, trabajo_habilidad.id_habilidad))
            nuevo_id = cursor.fetchone()["id_trabajo_habilidad"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_trabajo_habilidad: int, trabajo_habilidad: TrabajoHabilidad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE trabajos_habilidades
                SET id_habilidad = %s
                WHERE id_trabajo_habilidad = %s AND estado = TRUE
                RETURNING id_trabajo_habilidad;
            """
            cursor.execute(query, (trabajo_habilidad.id_habilidad, id_trabajo_habilidad))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_trabajo_habilidad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE trabajos_habilidades SET estado = FALSE WHERE id_trabajo_habilidad = %s AND estado = TRUE "
                "RETURNING id_trabajo_habilidad;",
                (id_trabajo_habilidad,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

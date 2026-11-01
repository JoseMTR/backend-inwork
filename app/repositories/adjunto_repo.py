from app.core.database import Database
from app.models.adjunto import Adjunto


class AdjuntoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM adjuntos WHERE estado = TRUE ORDER BY id_adjunto ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_adjunto: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM adjuntos WHERE id_adjunto = %s AND estado = TRUE;", (id_adjunto,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, adjunto: Adjunto, id_subido_por: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO adjuntos (id_subido_por, tipo_entidad, id_entidad, url, tipo_mime)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_adjunto;
            """
            cursor.execute(query, (id_subido_por, adjunto.tipo_entidad, adjunto.id_entidad, adjunto.url, adjunto.tipo_mime))
            nuevo_id = cursor.fetchone()["id_adjunto"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_adjunto: int, adjunto: Adjunto):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE adjuntos
                SET url = %s,
                    tipo_mime = %s
                WHERE id_adjunto = %s AND estado = TRUE
                RETURNING id_adjunto;
            """
            cursor.execute(query, (adjunto.url, adjunto.tipo_mime, id_adjunto))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_adjunto: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE adjuntos SET estado = FALSE WHERE id_adjunto = %s AND estado = TRUE RETURNING id_adjunto;",
                (id_adjunto,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

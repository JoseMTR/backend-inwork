from app.core.database import Database
from app.models.verificacion_identidad import VerificacionIdentidad, VerificacionRevisar


class VerificacionIdentidadRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM verificacion_identidad WHERE estado = TRUE ORDER BY created DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM verificacion_identidad WHERE id_usuario = %s AND estado = TRUE ORDER BY created DESC;",
                (id_usuario,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_verificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM verificacion_identidad WHERE id_verificacion = %s AND estado = TRUE;",
                           (id_verificacion,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, verificacion: VerificacionIdentidad, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO verificacion_identidad (id_usuario, url_documento_frente, url_documento_reverso, url_selfie)
                VALUES (%s, %s, %s, %s) RETURNING id_verificacion;
            """
            cursor.execute(query, (id_usuario, verificacion.url_documento_frente,
                                   verificacion.url_documento_reverso, verificacion.url_selfie))
            nuevo_id = cursor.fetchone()["id_verificacion"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_verificacion: int, verificacion: VerificacionIdentidad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE verificacion_identidad
                SET url_documento_frente = %s, url_documento_reverso = %s, url_selfie = %s
                WHERE id_verificacion = %s AND estado = TRUE
                RETURNING id_verificacion;
            """
            cursor.execute(query, (verificacion.url_documento_frente, verificacion.url_documento_reverso,
                                   verificacion.url_selfie, id_verificacion))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def revisar(self, id_verificacion: int, datos: VerificacionRevisar, id_admin: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE verificacion_identidad
                SET estado_verificacion = %s, observacion = %s, id_admin_revisor = %s,
                    fecha_revision = CURRENT_TIMESTAMP
                WHERE id_verificacion = %s AND estado = TRUE
                RETURNING id_verificacion;
            """
            cursor.execute(query, (datos.estado_verificacion, datos.observacion, id_admin, id_verificacion))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_verificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE verificacion_identidad SET estado = FALSE WHERE id_verificacion = %s AND estado = TRUE "
                "RETURNING id_verificacion;",
                (id_verificacion,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

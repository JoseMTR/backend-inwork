from app.core.database import Database
from app.models.notificacion import Notificacion


class NotificacionRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notificaciones WHERE estado = TRUE ORDER BY created DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notificaciones WHERE id_usuario = %s AND estado = TRUE ORDER BY created DESC;",
                           (id_usuario,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_notificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notificaciones WHERE id_notificacion = %s AND estado = TRUE;",
                           (id_notificacion,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, notificacion: Notificacion):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO notificaciones (id_usuario, tipo, titulo, contenido, id_referencia)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_notificacion;
            """
            cursor.execute(query, (notificacion.id_usuario, notificacion.tipo, notificacion.titulo,
                                   notificacion.contenido, notificacion.id_referencia))
            nuevo_id = cursor.fetchone()["id_notificacion"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_notificacion: int, notificacion: Notificacion):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE notificaciones
                SET id_usuario = %s, tipo = %s, titulo = %s, contenido = %s, id_referencia = %s
                WHERE id_notificacion = %s AND estado = TRUE
                RETURNING id_notificacion;
            """
            cursor.execute(query, (notificacion.id_usuario, notificacion.tipo, notificacion.titulo,
                                   notificacion.contenido, notificacion.id_referencia, id_notificacion))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def marcar_leida(self, id_notificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE notificaciones SET leida = TRUE WHERE id_notificacion = %s;", (id_notificacion,))
            conn.commit()
        finally:
            conn.close()

    def eliminar(self, id_notificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notificaciones SET estado = FALSE WHERE id_notificacion = %s AND estado = TRUE "
                "RETURNING id_notificacion;",
                (id_notificacion,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

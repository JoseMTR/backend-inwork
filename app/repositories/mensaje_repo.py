from app.core.database import Database
from app.models.mensaje import Mensaje


class MensajeRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mensajes WHERE estado = TRUE ORDER BY id_mensaje ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_chat(self, id_chat: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mensajes WHERE id_chat = %s AND estado = TRUE ORDER BY created ASC;",
                           (id_chat,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_mensaje: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM mensajes WHERE id_mensaje = %s AND estado = TRUE;", (id_mensaje,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, mensaje: Mensaje, id_remitente: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO mensajes (id_chat, id_remitente, mensaje)
                VALUES (%s, %s, %s) RETURNING id_mensaje;
            """
            cursor.execute(query, (mensaje.id_chat, id_remitente, mensaje.mensaje))
            nuevo_id = cursor.fetchone()["id_mensaje"]
            # Se actualiza el chat para que quede de primero en la lista
            cursor.execute("UPDATE chat SET updated = CURRENT_TIMESTAMP WHERE id_chat = %s;", (mensaje.id_chat,))
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_mensaje: int, mensaje: Mensaje):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE mensajes SET mensaje = %s WHERE id_mensaje = %s AND estado = TRUE RETURNING id_mensaje;",
                (mensaje.mensaje, id_mensaje)
            )
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def marcar_leidos(self, id_chat: int, id_lector: int):
        """Marca como leidos los mensajes que le envio la otra persona."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE mensajes SET leido = TRUE WHERE id_chat = %s AND id_remitente <> %s AND leido = FALSE;",
                (id_chat, id_lector)
            )
            total = cursor.rowcount
            conn.commit()
            return total
        finally:
            conn.close()

    def eliminar(self, id_mensaje: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE mensajes SET estado = FALSE WHERE id_mensaje = %s AND estado = TRUE RETURNING id_mensaje;",
                (id_mensaje,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

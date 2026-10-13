from app.core.database import Database
from app.models.chat import Chat


class ChatRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat WHERE estado = TRUE ORDER BY updated DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT * FROM chat
                WHERE (id_cliente = %s OR id_trabajador = %s) AND estado = TRUE
                ORDER BY updated DESC;
            """
            cursor.execute(query, (id_usuario, id_usuario))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_chat: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat WHERE id_chat = %s AND estado = TRUE;", (id_chat,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, chat: Chat):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO chat (id_trabajo, id_cliente, id_trabajador)
                VALUES (%s, %s, %s) RETURNING id_chat;
            """
            cursor.execute(query, (chat.id_trabajo, chat.id_cliente, chat.id_trabajador))
            nuevo_id = cursor.fetchone()["id_chat"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def eliminar(self, id_chat: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE chat SET estado = FALSE WHERE id_chat = %s AND estado = TRUE RETURNING id_chat;",
                           (id_chat,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

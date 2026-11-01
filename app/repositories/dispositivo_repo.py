from app.core.database import Database
from app.models.dispositivo import Dispositivo


class DispositivoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dispositivos WHERE estado = TRUE ORDER BY id_dispositivo ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dispositivos WHERE id_usuario = %s AND estado = TRUE ORDER BY id_dispositivo ASC;", (id_usuario,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_dispositivo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dispositivos WHERE id_dispositivo = %s AND estado = TRUE;", (id_dispositivo,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, dispositivo: Dispositivo, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO dispositivos (id_usuario, token_push, plataforma)
                VALUES (%s, %s, %s) RETURNING id_dispositivo;
            """
            cursor.execute(query, (id_usuario, dispositivo.token_push, dispositivo.plataforma))
            nuevo_id = cursor.fetchone()["id_dispositivo"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_dispositivo: int, dispositivo: Dispositivo):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE dispositivos
                SET token_push = %s,
                    plataforma = %s
                WHERE id_dispositivo = %s AND estado = TRUE
                RETURNING id_dispositivo;
            """
            cursor.execute(query, (dispositivo.token_push, dispositivo.plataforma, id_dispositivo))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_dispositivo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE dispositivos SET estado = FALSE WHERE id_dispositivo = %s AND estado = TRUE RETURNING id_dispositivo;",
                (id_dispositivo,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

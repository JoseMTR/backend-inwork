import hashlib

from app.core.database import Database
from app.models.token_usuario import TokenUsuario

COLUMNAS = "id_token, id_usuario, tipo, expira, usado, created, updated, estado"


class TokenUsuarioRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {COLUMNAS} FROM tokens_usuario WHERE estado = TRUE ORDER BY id_token ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_token: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {COLUMNAS} FROM tokens_usuario WHERE id_token = %s AND estado = TRUE;", (id_token,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, token: TokenUsuario):
        token_hash = hashlib.sha256(token.token.encode("utf-8")).hexdigest()
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO tokens_usuario (id_usuario, tipo, token_hash, expira, usado)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_token;
            """
            cursor.execute(query, (token.id_usuario, token.tipo, token_hash, token.expira, token.usado))
            nuevo_id = cursor.fetchone()["id_token"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_token: int, token: TokenUsuario):
        token_hash = hashlib.sha256(token.token.encode("utf-8")).hexdigest()
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE tokens_usuario
                SET id_usuario = %s, tipo = %s, token_hash = %s, expira = %s, usado = %s
                WHERE id_token = %s AND estado = TRUE
                RETURNING id_token;
            """
            cursor.execute(query, (token.id_usuario, token.tipo, token_hash, token.expira, token.usado, id_token))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_token: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tokens_usuario SET estado = FALSE WHERE id_token = %s AND estado = TRUE RETURNING id_token;",
                (id_token,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

from app.core.database import Database
from app.models.usuario_habilidad import UsuarioHabilidad


class UsuarioHabilidadRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_habilidades WHERE estado = TRUE ORDER BY id_usuario_habilidad ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_usuario_habilidad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_habilidades WHERE id_usuario_habilidad = %s AND estado = TRUE;", (id_usuario_habilidad,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, usuario_habilidad: UsuarioHabilidad, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO usuarios_habilidades (id_usuario, id_habilidad, anios_experiencia)
                VALUES (%s, %s, %s) RETURNING id_usuario_habilidad;
            """
            cursor.execute(query, (id_usuario, usuario_habilidad.id_habilidad, usuario_habilidad.anios_experiencia))
            nuevo_id = cursor.fetchone()["id_usuario_habilidad"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_usuario_habilidad: int, usuario_habilidad: UsuarioHabilidad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE usuarios_habilidades
                SET id_habilidad = %s,
                    anios_experiencia = %s
                WHERE id_usuario_habilidad = %s AND estado = TRUE
                RETURNING id_usuario_habilidad;
            """
            cursor.execute(query, (usuario_habilidad.id_habilidad, usuario_habilidad.anios_experiencia, id_usuario_habilidad))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_usuario_habilidad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios_habilidades SET estado = FALSE WHERE id_usuario_habilidad = %s AND estado = TRUE RETURNING id_usuario_habilidad;",
                (id_usuario_habilidad,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

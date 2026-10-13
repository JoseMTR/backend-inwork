from app.core.database import Database
from app.models.modulo import Modulo


class ModuloRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM modulos WHERE estado = TRUE ORDER BY id_modulo ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_modulo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM modulos WHERE id_modulo = %s AND estado = TRUE;", (id_modulo,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, modulo: Modulo):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO modulos (nombre, descripcion)
                VALUES (%s, %s) RETURNING id_modulo;
            """
            cursor.execute(query, (modulo.nombre, modulo.descripcion))
            nuevo_id = cursor.fetchone()["id_modulo"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_modulo: int, modulo: Modulo):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE modulos
                SET nombre = %s,
                    descripcion = %s
                WHERE id_modulo = %s AND estado = TRUE
                RETURNING id_modulo;
            """
            cursor.execute(query, (modulo.nombre, modulo.descripcion, id_modulo))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_modulo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE modulos SET estado = FALSE WHERE id_modulo = %s AND estado = TRUE RETURNING id_modulo;",
                (id_modulo,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

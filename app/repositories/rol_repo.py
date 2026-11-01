from app.core.database import Database
from app.models.rol import Rol


class RolRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roles WHERE estado = TRUE ORDER BY id_rol ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_rol: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roles WHERE id_rol = %s AND estado = TRUE;", (id_rol,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, rol: Rol):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO roles (nombre, descripcion)
                VALUES (%s, %s) RETURNING id_rol;
            """
            cursor.execute(query, (rol.nombre, rol.descripcion))
            nuevo_id = cursor.fetchone()["id_rol"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_rol: int, rol: Rol):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE roles
                SET nombre = %s,
                    descripcion = %s
                WHERE id_rol = %s AND estado = TRUE
                RETURNING id_rol;
            """
            cursor.execute(query, (rol.nombre, rol.descripcion, id_rol))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_rol: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE roles SET estado = FALSE WHERE id_rol = %s AND estado = TRUE RETURNING id_rol;",
                (id_rol,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

from app.core.database import Database
from app.models.rol_modulo import RolModulo


class RolModuloRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rol_modulo WHERE estado = TRUE ORDER BY id_rol_modulo ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_rol_modulo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rol_modulo WHERE id_rol_modulo = %s AND estado = TRUE;", (id_rol_modulo,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, rol_modulo: RolModulo):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO rol_modulo (id_rol, id_modulo, puede_crear, puede_leer, puede_editar, puede_eliminar)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_rol_modulo;
            """
            cursor.execute(query, (rol_modulo.id_rol, rol_modulo.id_modulo, rol_modulo.puede_crear, rol_modulo.puede_leer, rol_modulo.puede_editar, rol_modulo.puede_eliminar))
            nuevo_id = cursor.fetchone()["id_rol_modulo"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_rol_modulo: int, rol_modulo: RolModulo):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE rol_modulo
                SET id_rol = %s,
                    id_modulo = %s,
                    puede_crear = %s,
                    puede_leer = %s,
                    puede_editar = %s,
                    puede_eliminar = %s
                WHERE id_rol_modulo = %s AND estado = TRUE
                RETURNING id_rol_modulo;
            """
            cursor.execute(query, (rol_modulo.id_rol, rol_modulo.id_modulo, rol_modulo.puede_crear, rol_modulo.puede_leer, rol_modulo.puede_editar, rol_modulo.puede_eliminar, id_rol_modulo))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_rol_modulo: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rol_modulo SET estado = FALSE WHERE id_rol_modulo = %s AND estado = TRUE RETURNING id_rol_modulo;",
                (id_rol_modulo,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

    def obtener_modulos_por_rol(self, id_rol: int):
        """Los modulos que puede ver un rol, segun la tabla rol_modulo. Con esto se arma el menu."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT m.nombre, m.descripcion, m.ruta,
                       rm.puede_crear, rm.puede_leer, rm.puede_editar, rm.puede_eliminar
                FROM rol_modulo rm
                INNER JOIN modulos m ON m.id_modulo = rm.id_modulo
                WHERE rm.id_rol = %s AND rm.puede_leer = TRUE
                  AND rm.estado = TRUE AND m.estado = TRUE
                ORDER BY m.id_modulo ASC;
            """
            cursor.execute(query, (id_rol,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_permiso(self, id_rol: int, nombre_modulo: str):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT rm.puede_crear, rm.puede_leer, rm.puede_editar, rm.puede_eliminar
                FROM rol_modulo rm
                INNER JOIN modulos m ON m.id_modulo = rm.id_modulo
                WHERE rm.id_rol = %s AND m.nombre = %s
                  AND rm.estado = TRUE AND m.estado = TRUE;
            """
            cursor.execute(query, (id_rol, nombre_modulo))
            return cursor.fetchone()
        finally:
            conn.close()

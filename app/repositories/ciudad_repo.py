from app.core.database import Database
from app.models.ciudad import Ciudad


class CiudadRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ciudades WHERE estado = TRUE ORDER BY id_ciudad ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_ciudad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ciudades WHERE id_ciudad = %s AND estado = TRUE;", (id_ciudad,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, ciudad: Ciudad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO ciudades (id_pais, nombre)
                VALUES (%s, %s) RETURNING id_ciudad;
            """
            cursor.execute(query, (ciudad.id_pais, ciudad.nombre))
            nuevo_id = cursor.fetchone()["id_ciudad"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_ciudad: int, ciudad: Ciudad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE ciudades
                SET id_pais = %s,
                    nombre = %s
                WHERE id_ciudad = %s AND estado = TRUE
                RETURNING id_ciudad;
            """
            cursor.execute(query, (ciudad.id_pais, ciudad.nombre, id_ciudad))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_ciudad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ciudades SET estado = FALSE WHERE id_ciudad = %s AND estado = TRUE RETURNING id_ciudad;",
                (id_ciudad,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

from app.core.database import Database
from app.models.habilidad import Habilidad


class HabilidadRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habilidades WHERE estado = TRUE ORDER BY id_habilidad ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_habilidad: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM habilidades WHERE id_habilidad = %s AND estado = TRUE;", (id_habilidad,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, habilidad: Habilidad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO habilidades (nombre, descripcion)
                VALUES (%s, %s) RETURNING id_habilidad;
            """
            cursor.execute(query, (habilidad.nombre, habilidad.descripcion))
            nuevo_id = cursor.fetchone()["id_habilidad"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_habilidad: int, habilidad: Habilidad):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE habilidades
                SET nombre = %s,
                    descripcion = %s
                WHERE id_habilidad = %s AND estado = TRUE
                RETURNING id_habilidad;
            """
            cursor.execute(query, (habilidad.nombre, habilidad.descripcion, id_habilidad))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_habilidad: int):
        # Borrado logico: no se borra la fila, solo se pone estado = FALSE
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE habilidades SET estado = FALSE WHERE id_habilidad = %s AND estado = TRUE RETURNING id_habilidad;",
                (id_habilidad,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

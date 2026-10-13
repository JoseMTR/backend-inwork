from app.core.database import Database
from app.models.pais import Pais


class PaisRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pais WHERE estado = TRUE ORDER BY id_pais ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_pais: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pais WHERE id_pais = %s AND estado = TRUE;", (id_pais,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, pais: Pais):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO pais (nombre)
                VALUES (%s) RETURNING id_pais;
            """
            cursor.execute(query, (pais.nombre))
            nuevo_id = cursor.fetchone()["id_pais"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_pais: int, pais: Pais):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE pais
                SET nombre = %s
                WHERE id_pais = %s AND estado = TRUE
                RETURNING id_pais;
            """
            cursor.execute(query, (pais.nombre, id_pais))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_pais: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pais SET estado = FALSE WHERE id_pais = %s AND estado = TRUE RETURNING id_pais;",
                (id_pais,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

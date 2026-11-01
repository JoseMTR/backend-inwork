from app.core.database import Database
from app.models.categoria import Categoria


class CategoriaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias WHERE estado = TRUE ORDER BY id_categoria ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_categoria: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias WHERE id_categoria = %s AND estado = TRUE;", (id_categoria,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, categoria: Categoria):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO categorias (nombre, descripcion)
                VALUES (%s, %s) RETURNING id_categoria;
            """
            cursor.execute(query, (categoria.nombre, categoria.descripcion))
            nuevo_id = cursor.fetchone()["id_categoria"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_categoria: int, categoria: Categoria):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE categorias
                SET nombre = %s,
                    descripcion = %s
                WHERE id_categoria = %s AND estado = TRUE
                RETURNING id_categoria;
            """
            cursor.execute(query, (categoria.nombre, categoria.descripcion, id_categoria))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_categoria: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categorias SET estado = FALSE WHERE id_categoria = %s AND estado = TRUE RETURNING id_categoria;",
                (id_categoria,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

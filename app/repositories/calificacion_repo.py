from app.core.database import Database
from app.models.calificacion import Calificacion


class CalificacionRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calificacion WHERE estado = TRUE ORDER BY id_calificacion ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_calificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calificacion WHERE id_calificacion = %s AND estado = TRUE;", (id_calificacion,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, calificacion: Calificacion, id_calificador: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO calificacion (id_calificador, id_calificado, id_trabajo, puntuacion, comentario)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_calificacion;
            """
            cursor.execute(query, (id_calificador, calificacion.id_calificado, calificacion.id_trabajo, calificacion.puntuacion, calificacion.comentario))
            nuevo_id = cursor.fetchone()["id_calificacion"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_calificacion: int, calificacion: Calificacion):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE calificacion
                SET puntuacion = %s,
                    comentario = %s
                WHERE id_calificacion = %s AND estado = TRUE
                RETURNING id_calificacion;
            """
            cursor.execute(query, (calificacion.puntuacion, calificacion.comentario, id_calificacion))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_calificacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE calificacion SET estado = FALSE WHERE id_calificacion = %s AND estado = TRUE RETURNING id_calificacion;",
                (id_calificacion,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

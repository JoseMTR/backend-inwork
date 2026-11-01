from app.core.database import Database
from app.models.reporte import Reporte, ReporteResolver


class ReporteRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reportes WHERE estado = TRUE ORDER BY created DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_reportante: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reportes WHERE id_reportante = %s AND estado = TRUE ORDER BY created DESC;",
                           (id_reportante,))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_reporte: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reportes WHERE id_reporte = %s AND estado = TRUE;", (id_reporte,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, reporte: Reporte, id_reportante: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO reportes (id_reportante, id_reportado, id_trabajo, motivo, descripcion)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_reporte;
            """
            cursor.execute(query, (id_reportante, reporte.id_reportado, reporte.id_trabajo,
                                   reporte.motivo, reporte.descripcion))
            nuevo_id = cursor.fetchone()["id_reporte"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_reporte: int, reporte: Reporte):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE reportes SET motivo = %s, descripcion = %s
                WHERE id_reporte = %s AND estado = TRUE
                RETURNING id_reporte;
            """
            cursor.execute(query, (reporte.motivo, reporte.descripcion, id_reporte))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def resolver(self, id_reporte: int, datos: ReporteResolver, id_admin: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE reportes
                SET estado_reporte = %s, resolucion = %s, id_admin_revisor = %s,
                    fecha_resolucion = CURRENT_TIMESTAMP
                WHERE id_reporte = %s AND estado = TRUE
                RETURNING id_reporte;
            """
            cursor.execute(query, (datos.estado_reporte, datos.resolucion, id_admin, id_reporte))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def eliminar(self, id_reporte: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reportes SET estado = FALSE WHERE id_reporte = %s AND estado = TRUE RETURNING id_reporte;",
                (id_reporte,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

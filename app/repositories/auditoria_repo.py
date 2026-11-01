from app.core.database import Database


class AuditoriaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM auditoria ORDER BY id_auditoria DESC LIMIT 200;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_auditoria: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM auditoria WHERE id_auditoria = %s;", (id_auditoria,))
            return cursor.fetchone()
        finally:
            conn.close()

    def registrar(self, id_usuario: int, tabla: str, id_registro: int, accion: str):
        """Guarda quien hizo que cosa. accion: INSERT, UPDATE o DELETE"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO auditoria (id_usuario, tabla, id_registro, accion)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (id_usuario, tabla, id_registro, accion))
            conn.commit()
        finally:
            conn.close()

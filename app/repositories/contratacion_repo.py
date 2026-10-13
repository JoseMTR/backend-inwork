from app.core.database import Database
from app.models.contratacion import Contratacion


class ContratacionRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contrataciones WHERE estado = TRUE ORDER BY id_contratacion DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_usuario: int):
        """Contrataciones donde el usuario es el cliente o el trabajador."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT * FROM contrataciones
                WHERE (id_cliente = %s OR id_trabajador = %s) AND estado = TRUE
                ORDER BY id_contratacion DESC;
            """
            cursor.execute(query, (id_usuario, id_usuario))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_contratacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contrataciones WHERE id_contratacion = %s AND estado = TRUE;", (id_contratacion,))
            return cursor.fetchone()
        finally:
            conn.close()

    def datos_para_custodia(self, id_contratacion: int):
        """Los datos que necesita la API de pagos para crear la custodia."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT c.id_contratacion, uc.correo AS correo_cliente,
                       ut.correo AS correo_trabajador, o.valor_oferta AS monto
                FROM contrataciones c
                INNER JOIN usuarios uc ON uc.id_usuario = c.id_cliente
                INNER JOIN usuarios ut ON ut.id_usuario = c.id_trabajador
                INNER JOIN ofertas o ON o.id_oferta = c.id_oferta
                WHERE c.id_contratacion = %s;
            """
            cursor.execute(query, (id_contratacion,))
            fila = cursor.fetchone()
            return {
                "id_contratacion": fila["id_contratacion"],
                "correo_cliente": fila["correo_cliente"],
                "correo_trabajador": fila["correo_trabajador"],
                "monto": float(fila["monto"]),
            }
        finally:
            conn.close()

    def crear(self, contratacion: Contratacion):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO contrataciones (id_trabajo, id_cliente, id_trabajador, id_oferta)
                VALUES (%s, %s, %s, %s) RETURNING id_contratacion;
            """
            cursor.execute(query, (contratacion.id_trabajo, contratacion.id_cliente,
                                   contratacion.id_trabajador, contratacion.id_oferta))
            nuevo_id = cursor.fetchone()["id_contratacion"]
            cursor.execute("UPDATE ofertas SET estado_oferta = 'aceptada' WHERE id_oferta = %s;",
                           (contratacion.id_oferta,))
            cursor.execute("UPDATE trabajos SET estado_trabajo = 'asignado' WHERE id_trabajo = %s;",
                           (contratacion.id_trabajo,))
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_contratacion: int, estado_contratacion: str):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE contrataciones SET estado_contratacion = %s
                WHERE id_contratacion = %s AND estado = TRUE
                RETURNING id_contratacion;
            """
            cursor.execute(query, (estado_contratacion, id_contratacion))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def finalizar(self, contratacion: dict):
        """Contratacion y trabajo pasan a 'finalizado' y se avisa al trabajador."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE contrataciones SET estado_contratacion = 'finalizada' WHERE id_contratacion = %s;",
                           (contratacion["id_contratacion"],))
            cursor.execute("UPDATE trabajos SET estado_trabajo = 'finalizado' WHERE id_trabajo = %s;",
                           (contratacion["id_trabajo"],))
            cursor.execute(
                """
                INSERT INTO notificaciones (id_usuario, tipo, titulo, contenido, id_referencia)
                VALUES (%s, 'contratacion_finalizada', 'Trabajo finalizado',
                        'El trabajo fue finalizado. Ya puedes calificar al cliente.', %s);
                """,
                (contratacion["id_trabajador"], contratacion["id_contratacion"])
            )
            conn.commit()
        finally:
            conn.close()

    def cancelar(self, contratacion: dict, id_quien_cancela: int):
        """La contratacion se cancela y el trabajo vuelve a 'publicado'."""
        otro = contratacion["id_trabajador"]
        if id_quien_cancela == contratacion["id_trabajador"]:
            otro = contratacion["id_cliente"]

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE contrataciones SET estado_contratacion = 'cancelada' WHERE id_contratacion = %s;",
                           (contratacion["id_contratacion"],))
            cursor.execute("UPDATE trabajos SET estado_trabajo = 'publicado' WHERE id_trabajo = %s;",
                           (contratacion["id_trabajo"],))
            cursor.execute(
                """
                INSERT INTO notificaciones (id_usuario, tipo, titulo, contenido, id_referencia)
                VALUES (%s, 'contratacion_cancelada', 'Contratacion cancelada',
                        'La contratacion fue cancelada.', %s);
                """,
                (otro, contratacion["id_contratacion"])
            )
            conn.commit()
        finally:
            conn.close()

    def eliminar(self, id_contratacion: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contrataciones SET estado = FALSE WHERE id_contratacion = %s AND estado = TRUE "
                "RETURNING id_contratacion;",
                (id_contratacion,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

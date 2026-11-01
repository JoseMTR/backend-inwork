from app.core.database import Database
from app.models.oferta import Oferta


class OfertaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ofertas WHERE estado = TRUE ORDER BY id_oferta DESC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_usuario(self, id_usuario: int):
        """Las ofertas que hizo el usuario y las que recibio en sus trabajos."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT o.* FROM ofertas o
                INNER JOIN trabajos t ON t.id_trabajo = o.id_trabajo
                WHERE (o.id_trabajador = %s OR t.id_cliente = %s) AND o.estado = TRUE
                ORDER BY o.id_oferta DESC;
            """
            cursor.execute(query, (id_usuario, id_usuario))
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_oferta: int):
        """Trae la oferta junto con el dueno y el estado del trabajo."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT o.*, t.id_cliente, t.estado_trabajo, t.titulo
                FROM ofertas o
                INNER JOIN trabajos t ON t.id_trabajo = o.id_trabajo
                WHERE o.id_oferta = %s AND o.estado = TRUE;
            """
            cursor.execute(query, (id_oferta,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, oferta: Oferta, id_trabajador: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO ofertas (id_trabajo, id_trabajador, valor_oferta, moneda, mensaje)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_oferta;
            """
            cursor.execute(query, (oferta.id_trabajo, id_trabajador, oferta.valor_oferta, oferta.moneda, oferta.mensaje))
            nuevo_id = cursor.fetchone()["id_oferta"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_oferta: int, oferta: Oferta):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE ofertas
                SET valor_oferta = %s, moneda = %s, mensaje = %s
                WHERE id_oferta = %s AND estado = TRUE
                RETURNING id_oferta;
            """
            cursor.execute(query, (oferta.valor_oferta, oferta.moneda, oferta.mensaje, id_oferta))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def aceptar(self, oferta: dict):
        
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE ofertas SET estado_oferta = 'aceptada' WHERE id_oferta = %s;",
                           (oferta["id_oferta"],))
            cursor.execute(
                """
                UPDATE ofertas SET estado_oferta = 'rechazada'
                WHERE id_trabajo = %s AND id_oferta <> %s AND estado_oferta = 'pendiente';
                """,
                (oferta["id_trabajo"], oferta["id_oferta"])
            )
            cursor.execute("UPDATE trabajos SET estado_trabajo = 'asignado' WHERE id_trabajo = %s;",
                           (oferta["id_trabajo"],))
            cursor.execute(
                """
                INSERT INTO contrataciones (id_trabajo, id_cliente, id_trabajador, id_oferta)
                VALUES (%s, %s, %s, %s) RETURNING id_contratacion;
                """,
                (oferta["id_trabajo"], oferta["id_cliente"], oferta["id_trabajador"], oferta["id_oferta"])
            )
            id_contratacion = cursor.fetchone()["id_contratacion"]
            cursor.execute(
                """
                INSERT INTO notificaciones (id_usuario, tipo, titulo, contenido, id_referencia)
                VALUES (%s, 'oferta_aceptada', 'Tu oferta fue aceptada', %s, %s);
                """,
                (oferta["id_trabajador"], f"Fuiste contratado para: {oferta['titulo']}", id_contratacion)
            )
            conn.commit()
            return id_contratacion
        finally:
            conn.close()

    def retirar(self, id_oferta: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE ofertas SET estado_oferta = 'retirada' WHERE id_oferta = %s;", (id_oferta,))
            conn.commit()
        finally:
            conn.close()

    def eliminar(self, id_oferta: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ofertas SET estado = FALSE WHERE id_oferta = %s AND estado = TRUE RETURNING id_oferta;",
                (id_oferta,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

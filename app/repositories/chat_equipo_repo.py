from app.core.database import Database

# Cada mensaje se devuelve con el nombre y el rol de quien lo escribio,
# asi el frontend no tiene que buscar el usuario aparte.
CONSULTA_MENSAJES = """
    SELECT m.id_mensaje_equipo, m.id_remitente, m.mensaje, m.created,
           u.nombre || ' ' || u.apellido AS nombre,
           r.nombre AS rol
    FROM mensajes_equipo m
    JOIN usuarios u ON u.id_usuario = m.id_remitente
    JOIN roles r ON r.id_rol = u.id_rol
"""


def fecha_a_texto(fila: dict) -> dict:
    """El WebSocket envia JSON y el JSON no entiende fechas de Python: se pasan a texto (ISO)."""
    if fila and fila.get("created") is not None:
        fila["created"] = fila["created"].isoformat()
    return fila


class ChatEquipoRepository:
    def __init__(self):
        self.db = Database()

    def ultimos_mensajes(self, limite: int = 50):
        """Los ultimos mensajes del chat del equipo, del mas viejo al mas nuevo."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = CONSULTA_MENSAJES + """
                WHERE m.estado = TRUE
                ORDER BY m.created DESC, m.id_mensaje_equipo DESC
                LIMIT %s;
            """
            cursor.execute(query, (limite,))
            filas = [fecha_a_texto(dict(f)) for f in cursor.fetchall()]
            filas.reverse()
            return filas
        finally:
            conn.close()

    def crear(self, id_remitente: int, mensaje: str):
        """Guarda el mensaje y lo devuelve completo (con nombre, rol y fecha)."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO mensajes_equipo (id_remitente, mensaje) VALUES (%s, %s) RETURNING id_mensaje_equipo;",
                (id_remitente, mensaje)
            )
            nuevo_id = cursor.fetchone()["id_mensaje_equipo"]
            conn.commit()
            cursor.execute(CONSULTA_MENSAJES + " WHERE m.id_mensaje_equipo = %s;", (nuevo_id,))
            return fecha_a_texto(dict(cursor.fetchone()))
        finally:
            conn.close()

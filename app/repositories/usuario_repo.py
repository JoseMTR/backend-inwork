from app.core.database import Database
from app.models.usuario import UsuarioActualizar, UsuarioRegistro

# Columnas que se devuelven (NUNCA se devuelve el password)
COLUMNAS = """
    id_usuario, id_rol, id_ciudad, nombre, apellido, foto_perfil, correo,
    correo_verificado, telefono, tipo_identificacion, numero_identificacion,
    fecha_nacimiento, descripcion, direccion, promedio_calificacion,
    total_calificaciones, created, updated, estado
"""


class UsuarioRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {COLUMNAS} FROM usuarios WHERE estado = TRUE ORDER BY id_usuario ASC;")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_por_id(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {COLUMNAS} FROM usuarios WHERE id_usuario = %s AND estado = TRUE;", (id_usuario,))
            return cursor.fetchone()
        finally:
            conn.close()

    def obtener_por_correo(self, correo: str):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE correo = %s;", (correo,))
            return cursor.fetchone()
        finally:
            conn.close()

    def obtener_perfil_publico(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT u.id_usuario, u.nombre, u.apellido, u.foto_perfil, u.descripcion,
                       u.promedio_calificacion, u.total_calificaciones, c.nombre AS ciudad
                FROM usuarios u
                LEFT JOIN ciudades c ON c.id_ciudad = u.id_ciudad
                WHERE u.id_usuario = %s AND u.estado = TRUE;
            """
            cursor.execute(query, (id_usuario,))
            return cursor.fetchone()
        finally:
            conn.close()

    def crear(self, usuario: UsuarioRegistro, password_encriptada: str, id_rol: int = 3):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO usuarios (id_rol, id_ciudad, nombre, apellido, password, foto_perfil,
                                      correo, telefono, tipo_identificacion, numero_identificacion,
                                      fecha_nacimiento, descripcion, direccion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_usuario;
            """
            cursor.execute(query, (
                id_rol, usuario.id_ciudad, usuario.nombre, usuario.apellido, password_encriptada,
                usuario.foto_perfil, usuario.correo.lower(), usuario.telefono,
                usuario.tipo_identificacion, usuario.numero_identificacion,
                usuario.fecha_nacimiento, usuario.descripcion, usuario.direccion
            ))
            nuevo_id = cursor.fetchone()["id_usuario"]
            conn.commit()
            return nuevo_id
        finally:
            conn.close()

    def actualizar(self, id_usuario: int, usuario: UsuarioActualizar):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                UPDATE usuarios
                SET id_ciudad = %s, nombre = %s, apellido = %s, telefono = %s,
                    foto_perfil = %s, descripcion = %s, direccion = %s
                WHERE id_usuario = %s AND estado = TRUE
                RETURNING id_usuario;
            """
            cursor.execute(query, (
                usuario.id_ciudad, usuario.nombre, usuario.apellido, usuario.telefono,
                usuario.foto_perfil, usuario.descripcion, usuario.direccion, id_usuario
            ))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def cambiar_rol(self, id_usuario: int, id_rol: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET id_rol = %s WHERE id_usuario = %s AND estado = TRUE RETURNING id_usuario;",
                (id_rol, id_usuario)
            )
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        finally:
            conn.close()

    def cambiar_password(self, id_usuario: int, password_encriptada: str):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET password = %s WHERE id_usuario = %s;", (password_encriptada, id_usuario))
            conn.commit()
        finally:
            conn.close()

    def eliminar(self, id_usuario: int):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET estado = FALSE WHERE id_usuario = %s AND estado = TRUE RETURNING id_usuario;",
                (id_usuario,)
            )
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        finally:
            conn.close()

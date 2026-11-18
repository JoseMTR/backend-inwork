# Gestor de conexiones del chat del equipo (WebSocket).
# Guarda en memoria quien esta conectado y le reparte cada mensaje a todos.
#
# Cada conexion es: {"socket": <WebSocket>, "usuario": {"id_usuario", "nombre", "rol"}}
# Un mismo usuario puede tener varias pestanas abiertas: cada pestana es una conexion,
# pero en la lista de "conectados" aparece una sola vez.


class GestorChat:
    def __init__(self):
        self.conexiones = []

    def agregar(self, socket, usuario: dict) -> bool:
        """Agrega la conexion. Devuelve True si el usuario no tenia otra pestana abierta (acaba de entrar)."""
        ya_estaba = any(c["usuario"]["id_usuario"] == usuario["id_usuario"] for c in self.conexiones)
        self.conexiones.append({"socket": socket, "usuario": usuario})
        return not ya_estaba

    def quitar(self, socket) -> bool:
        """Quita la conexion. Devuelve True si era la ultima pestana del usuario (acaba de salir)."""
        conexion = next((c for c in self.conexiones if c["socket"] is socket), None)
        if conexion is None:
            return False
        self.conexiones.remove(conexion)
        id_usuario = conexion["usuario"]["id_usuario"]
        return not any(c["usuario"]["id_usuario"] == id_usuario for c in self.conexiones)

    def usuarios_conectados(self) -> list:
        """Lista de usuarios conectados sin repetir (aunque tengan varias pestanas)."""
        vistos = {}
        for c in self.conexiones:
            vistos[c["usuario"]["id_usuario"]] = c["usuario"]
        return list(vistos.values())

    async def enviar_a(self, socket, datos: dict):
        """Le envia un mensaje (JSON) a una sola conexion."""
        try:
            await socket.send_json(datos)
        except Exception:
            # Si esa pestana ya se cerro no pasa nada: su propio ciclo la quita de la lista
            pass

    async def enviar_a_todos(self, datos: dict):
        """Le envia el mismo mensaje (JSON) a todas las conexiones abiertas."""
        for c in list(self.conexiones):
            await self.enviar_a(c["socket"], datos)

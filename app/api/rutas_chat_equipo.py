# CHAT DEL EQUIPO EN TIEMPO REAL (WebSocket)
# Lo usan los usuarios del panel de administracion: Administrador, Moderador y Analista.
#
# El frontend (Angular) se conecta a:   ws://localhost:8000/ws/chat-equipo?token=<JWT>
# (en Render es wss://backend-inwork.onrender.com/ws/chat-equipo?token=<JWT>)
# El token va en la URL porque el navegador no deja poner el encabezado Authorization en un WebSocket.
#
# Mensajes que manda el frontend:
#   {"tipo": "mensaje", "texto": "Hola equipo"}
#
# Mensajes que manda la API:
#   {"tipo": "historial",  "mensajes": [...]}      solo al que se acaba de conectar
#   {"tipo": "mensaje",    "mensaje": {...}}        a todos, cada vez que alguien escribe
#   {"tipo": "conectados", "usuarios": [...]}       a todos, cuando alguien entra o sale
#   {"tipo": "aviso",      "texto": "...", "created": "..."}   "Mariana se unio al chat", etc.
#   {"tipo": "error",      "texto": "..."}          solo al que causo el error

import json
from datetime import datetime, timezone

import psycopg2
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from app.core.seguridad import ROL_ADMIN, ROL_ANALISTA, ROL_MODERADOR, obtener_usuario_actual, usuario_desde_token
from app.repositories.chat_equipo_repo import ChatEquipoRepository
from app.websocket.gestor_chat import GestorChat

router = APIRouter(tags=["Chat del equipo (WebSocket)"])
repo = ChatEquipoRepository()
gestor = GestorChat()   # uno solo para toda la API: aqui estan todas las conexiones abiertas

ROLES_CHAT = (ROL_ADMIN, ROL_MODERADOR, ROL_ANALISTA)
MAXIMO_CARACTERES = 1000

# Codigos de cierre propios (del 4000 al 4999 los puede usar cada aplicacion)
CIERRE_TOKEN_INVALIDO = 4401
CIERRE_SIN_PERMISO = 4403


def solo_equipo(usuario: dict):
    if usuario["id_rol"] not in ROLES_CHAT:
        raise HTTPException(status_code=403, detail="El chat es solo para administradores, moderadores y analistas")


def aviso(texto: str) -> dict:
    return {"tipo": "aviso", "texto": texto, "created": datetime.now(timezone.utc).isoformat()}


# ---------- Rutas normales (HTTP), utiles para revisar desde Swagger ----------

@router.get("/chat-equipo/mensajes")
def historial_chat_equipo(usuario: dict = Depends(obtener_usuario_actual)):
    """Ultimos 50 mensajes del chat del equipo."""
    solo_equipo(usuario)
    return repo.ultimos_mensajes()


@router.get("/chat-equipo/conectados")
def conectados_chat_equipo(usuario: dict = Depends(obtener_usuario_actual)):
    """Quienes tienen el chat abierto en este momento."""
    solo_equipo(usuario)
    return gestor.usuarios_conectados()


# ---------- WebSocket ----------

@router.websocket("/ws/chat-equipo")
async def chat_equipo(websocket: WebSocket):
    # Se acepta primero para poder decirle al navegador POR QUE se cierra si el token no sirve
    await websocket.accept()

    # 1. Revisar el token (el mismo JWT del login)
    token = websocket.query_params.get("token", "")
    try:
        # run_in_threadpool: la consulta a la BD no frena a los demas usuarios conectados
        usuario = await run_in_threadpool(usuario_desde_token, token)
    except HTTPException as error:
        await websocket.send_json({"tipo": "error", "texto": error.detail})
        await websocket.close(code=CIERRE_TOKEN_INVALIDO)
        return

    if usuario["id_rol"] not in ROLES_CHAT:
        await websocket.send_json({"tipo": "error", "texto": "El chat es solo para administradores, moderadores y analistas"})
        await websocket.close(code=CIERRE_SIN_PERMISO)
        return

    yo = {
        "id_usuario": usuario["id_usuario"],
        "nombre": f"{usuario['nombre']} {usuario['apellido']}",
        "rol": usuario["rol"],
    }

    # 2. Registrar la conexion y mandarle el historial
    acaba_de_entrar = gestor.agregar(websocket, yo)
    try:
        historial = await run_in_threadpool(repo.ultimos_mensajes)
    except psycopg2.Error:
        historial = []
        await gestor.enviar_a(websocket, {"tipo": "error", "texto": "No se pudo cargar el historial del chat"})
    await gestor.enviar_a(websocket, {"tipo": "historial", "mensajes": historial})

    # 3. Avisarles a todos que entro y la nueva lista de conectados
    if acaba_de_entrar:
        await gestor.enviar_a_todos(aviso(f"{yo['nombre']} ({yo['rol']}) se unio al chat"))
    await gestor.enviar_a_todos({"tipo": "conectados", "usuarios": gestor.usuarios_conectados()})

    # 4. Escuchar los mensajes de este usuario mientras la conexion siga abierta
    try:
        while True:
            texto_recibido = await websocket.receive_text()
            try:
                datos = json.loads(texto_recibido)
            except json.JSONDecodeError:
                await gestor.enviar_a(websocket, {"tipo": "error", "texto": "El mensaje debe ser JSON"})
                continue

            if not isinstance(datos, dict) or datos.get("tipo") != "mensaje":
                continue
            texto = str(datos.get("texto", "")).strip()
            if not texto:
                continue
            if len(texto) > MAXIMO_CARACTERES:
                await gestor.enviar_a(websocket, {"tipo": "error", "texto": f"El mensaje no puede pasar de {MAXIMO_CARACTERES} caracteres"})
                continue

            # Se guarda en la base de datos y se reparte a TODOS (tambien al que lo envio)
            try:
                nuevo = await run_in_threadpool(repo.crear, yo["id_usuario"], texto)
            except psycopg2.Error:
                await gestor.enviar_a(websocket, {"tipo": "error", "texto": "No se pudo guardar el mensaje, intenta de nuevo"})
                continue
            await gestor.enviar_a_todos({"tipo": "mensaje", "mensaje": nuevo})

    except WebSocketDisconnect:
        pass  # el usuario cerro la pestana, salio del chat o perdio internet

    finally:
        # 5. Desconexion: se quita de la lista y se les avisa a los demas
        acaba_de_salir = gestor.quitar(websocket)
        if acaba_de_salir:
            await gestor.enviar_a_todos(aviso(f"{yo['nombre']} ({yo['rol']}) salio del chat"))
        await gestor.enviar_a_todos({"tipo": "conectados", "usuarios": gestor.usuarios_conectados()})

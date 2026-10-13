from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, solo_staff, verificar_dueno, verificar_permiso
from app.models.mensaje import Mensaje
from app.repositories.chat_repo import ChatRepository
from app.repositories.mensaje_repo import MensajeRepository

router = APIRouter(prefix="/mensajes", tags=["Mensajes"])
repo = MensajeRepository()
chat_repo = ChatRepository()


def verificar_participante(usuario: dict, id_chat: int):
    chat = chat_repo.obtener_por_id(id_chat)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    if usuario["id_usuario"] not in (chat["id_cliente"], chat["id_trabajador"]) and not es_staff(usuario):
        raise HTTPException(status_code=403, detail="No participas en este chat")


@router.get("/")
def listar_mensajes(usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    return repo.obtener_todos()


@router.get("/chat/{id_chat}")
def mensajes_de_un_chat(id_chat: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "leer")
    verificar_participante(usuario, id_chat)
    return repo.obtener_por_chat(id_chat)


@router.put("/chat/{id_chat}/leidos")
def marcar_leidos(id_chat: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "editar")
    verificar_participante(usuario, id_chat)
    total = repo.marcar_leidos(id_chat, usuario["id_usuario"])
    return {"mensaje": "Mensajes marcados como leidos", "total": total}


@router.get("/{id_mensaje}")
def obtener_mensaje(id_mensaje: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "leer")
    mensaje = repo.obtener_por_id(id_mensaje)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    verificar_participante(usuario, mensaje["id_chat"])
    return mensaje


@router.post("/")
def enviar_mensaje(mensaje: Mensaje, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "crear")
    verificar_participante(usuario, mensaje.id_chat)
    nuevo_id = repo.crear(mensaje, usuario["id_usuario"])
    return {"mensaje": "Mensaje enviado", "id": nuevo_id}


@router.put("/{id_mensaje}")
def editar_mensaje(id_mensaje: int, mensaje: Mensaje, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "editar")
    actual = repo.obtener_por_id(id_mensaje)
    if not actual:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    verificar_dueno(usuario, actual["id_remitente"])
    repo.actualizar(id_mensaje, mensaje)
    return {"mensaje": "Mensaje editado correctamente"}


@router.delete("/{id_mensaje}")
def eliminar_mensaje(id_mensaje: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "eliminar")
    actual = repo.obtener_por_id(id_mensaje)
    if not actual:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    verificar_dueno(usuario, actual["id_remitente"])
    repo.eliminar(id_mensaje)
    return {"mensaje": "Mensaje eliminado correctamente"}

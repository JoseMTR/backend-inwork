from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, verificar_permiso
from app.models.chat import Chat
from app.repositories.chat_repo import ChatRepository

router = APIRouter(prefix="/chats", tags=["Chat"])
repo = ChatRepository()



def verificar_participante(usuario: dict, chat: dict):
    if usuario["id_usuario"] not in (chat["id_cliente"], chat["id_trabajador"]) and not es_staff(usuario):
        raise HTTPException(status_code=403, detail="No participas en este chat")


@router.get("/")
def listar_chats(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "leer")
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_chat}")
def obtener_chat(id_chat: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "leer")
    chat = repo.obtener_por_id(id_chat)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    verificar_participante(usuario, chat)
    return chat


@router.post("/")
def crear_chat(chat: Chat, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "crear")
    verificar_participante(usuario, chat.model_dump())
    nuevo_id = repo.crear(chat)
    return {"mensaje": "Chat creado exitosamente", "id": nuevo_id}


@router.delete("/{id_chat}")
def eliminar_chat(id_chat: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "chat", "eliminar")
    chat = repo.obtener_por_id(id_chat)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    verificar_participante(usuario, chat)
    repo.eliminar(id_chat)
    return {"mensaje": "Chat eliminado correctamente"}

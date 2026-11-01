from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.token_usuario import TokenUsuario
from app.repositories.token_usuario_repo import TokenUsuarioRepository

router = APIRouter(prefix="/tokens-usuario", tags=["Tokens de usuario"])
repo = TokenUsuarioRepository()


@router.get("/")
def listar_tokens(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "seguridad", "leer")
    return repo.obtener_todos()


@router.get("/{id_token}")
def obtener_token(id_token: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "seguridad", "leer")
    token = repo.obtener_por_id(id_token)
    if not token:
        raise HTTPException(status_code=404, detail="Token no encontrado")
    return token


@router.post("/")
def crear_token(token: TokenUsuario, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "seguridad", "crear")
    nuevo_id = repo.crear(token)
    return {"mensaje": "Token registrado exitosamente", "id": nuevo_id}


@router.put("/{id_token}")
def actualizar_token(id_token: int, token: TokenUsuario, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "seguridad", "editar")
    exito = repo.actualizar(id_token, token)
    if not exito:
        raise HTTPException(status_code=404, detail="Token no encontrado")
    return {"mensaje": "Token actualizado correctamente"}


@router.delete("/{id_token}")
def eliminar_token(id_token: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "seguridad", "eliminar")
    exito = repo.eliminar(id_token)
    if not exito:
        raise HTTPException(status_code=404, detail="Token no encontrado")
    return {"mensaje": "Token eliminado correctamente"}

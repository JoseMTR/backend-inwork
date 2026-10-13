from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import (
    encriptar_password,
    es_admin,
    obtener_usuario_actual,
    solo_staff,
    verificar_dueno,
    verificar_permiso,
)
from app.models.usuario import CambiarRol, UsuarioActualizar, UsuarioRegistro
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
repo = UsuarioRepository()
auditoria = AuditoriaRepository()


@router.get("/")
def listar_usuarios(usuario: dict = Depends(obtener_usuario_actual)):
    # La lista completa (con documentos y telefonos) solo la ve el staff
    solo_staff(usuario)
    return repo.obtener_todos()


@router.get("/{id_usuario}")
def obtener_usuario(id_usuario: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "leer")
    verificar_dueno(usuario, id_usuario)
    encontrado = repo.obtener_por_id(id_usuario)
    if not encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return encontrado


@router.get("/{id_usuario}/perfil")
def perfil_publico(id_usuario: int, usuario: dict = Depends(obtener_usuario_actual)):
    perfil = repo.obtener_perfil_publico(id_usuario)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return perfil


@router.post("/")
def crear_usuario(nuevo: UsuarioRegistro, id_rol: int = 3, usuario: dict = Depends(obtener_usuario_actual)):
    """El administrador crea usuarios eligiendo el rol (1 admin, 2 moderador, 3 usuario)."""
    if not es_admin(usuario):
        raise HTTPException(status_code=403, detail="Solo el administrador puede crear usuarios")
    nuevo_id = repo.crear(nuevo, encriptar_password(nuevo.password), id_rol)
    auditoria.registrar(usuario["id_usuario"], "usuarios", nuevo_id, "INSERT")
    return {"mensaje": "Usuario registrado exitosamente", "id": nuevo_id}


@router.put("/{id_usuario}")
def actualizar_usuario(id_usuario: int, datos: UsuarioActualizar, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "editar")
    verificar_dueno(usuario, id_usuario)
    exito = repo.actualizar(id_usuario, datos)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    auditoria.registrar(usuario["id_usuario"], "usuarios", id_usuario, "UPDATE")
    return {"mensaje": "Usuario actualizado correctamente"}


@router.put("/{id_usuario}/rol")
def cambiar_rol(id_usuario: int, datos: CambiarRol, usuario: dict = Depends(obtener_usuario_actual)):
    if not es_admin(usuario):
        raise HTTPException(status_code=403, detail="Solo el administrador puede cambiar roles")
    exito = repo.cambiar_rol(id_usuario, datos.id_rol)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    auditoria.registrar(usuario["id_usuario"], "usuarios", id_usuario, "UPDATE")
    return {"mensaje": "Rol actualizado correctamente"}


@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "eliminar")
    verificar_dueno(usuario, id_usuario)
    exito = repo.eliminar(id_usuario)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    auditoria.registrar(usuario["id_usuario"], "usuarios", id_usuario, "DELETE")
    return {"mensaje": "Usuario desactivado correctamente"}

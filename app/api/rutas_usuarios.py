from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import (
    ROLES_VALIDOS,
    encriptar_password,
    es_admin,
    obtener_usuario_actual,
    ve_todo,
    verificar_dueno,
    verificar_permiso,
)
from app.models.usuario import CambiarRol, RestablecerPassword, UsuarioActualizar, UsuarioRegistro
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.usuario_repo import UsuarioRepository

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
repo = UsuarioRepository()
auditoria = AuditoriaRepository()


@router.get("/")
def listar_usuarios(usuario: dict = Depends(obtener_usuario_actual)):
    # La lista completa (con documentos y telefonos) solo la ven administrador, moderador y analista
    if not ve_todo(usuario):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver todos los usuarios")
    return repo.obtener_todos()


@router.get("/{id_usuario}")
def obtener_usuario(id_usuario: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "leer")
    verificar_dueno(usuario, id_usuario, solo_lectura=True)
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


def validar_rol(id_rol: int):
    if id_rol not in ROLES_VALIDOS:
        raise HTTPException(status_code=400, detail="Roles validos: 1 Administrador, 2 Moderador, "
                                                    "3 Analista, 4 Empleador, 5 Empleado")


@router.post("/")
def crear_usuario(nuevo: UsuarioRegistro, usuario: dict = Depends(obtener_usuario_actual)):
    """El administrador crea usuarios con cualquier rol (campo id_rol, ej: 2 para un moderador)."""
    if not es_admin(usuario):
        raise HTTPException(status_code=403, detail="Solo el administrador puede crear usuarios")
    if len(nuevo.password) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener minimo 8 caracteres")
    validar_rol(nuevo.id_rol)
    nuevo_id = repo.crear(nuevo, encriptar_password(nuevo.password), nuevo.id_rol)
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
    """El administrador le cambia el rol a cualquier usuario, ej: {"id_rol": 2}"""
    if not es_admin(usuario):
        raise HTTPException(status_code=403, detail="Solo el administrador puede cambiar roles")
    if id_usuario == usuario["id_usuario"]:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol de administrador")
    validar_rol(datos.id_rol)
    exito = repo.cambiar_rol(id_usuario, datos.id_rol)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    auditoria.registrar(usuario["id_usuario"], "usuarios", id_usuario, "UPDATE")
    return {"mensaje": "Rol actualizado correctamente"}


@router.put("/{id_usuario}/password")
def restablecer_password(id_usuario: int, datos: RestablecerPassword, usuario: dict = Depends(obtener_usuario_actual)):
    """El administrador le pone una contrasena nueva a cualquier usuario."""
    if not es_admin(usuario):
        raise HTTPException(status_code=403, detail="Solo el administrador puede cambiar contrasenas de otros")
    if len(datos.password_nueva) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener minimo 8 caracteres")
    if not repo.obtener_por_id(id_usuario):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    repo.cambiar_password(id_usuario, encriptar_password(datos.password_nueva))
    auditoria.registrar(usuario["id_usuario"], "usuarios", id_usuario, "UPDATE")
    return {"mensaje": "Contrasena restablecida correctamente"}


@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "eliminar")
    verificar_dueno(usuario, id_usuario)
    exito = repo.eliminar(id_usuario)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    auditoria.registrar(usuario["id_usuario"], "usuarios", id_usuario, "DELETE")
    return {"mensaje": "Usuario desactivado correctamente"}

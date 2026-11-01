from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.rol import Rol
from app.repositories.rol_repo import RolRepository

router = APIRouter(prefix="/roles", tags=["Roles"])
repo = RolRepository()


@router.get("/")
def listar_roles(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "leer")
    return repo.obtener_todos()


@router.get("/{id_rol}")
def obtener_rol(id_rol: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "leer")
    rol = repo.obtener_por_id(id_rol)
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.post("/")
def crear_rol(rol: Rol, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "crear")
    nuevo_id = repo.crear(rol)
    return {"mensaje": "Rol registrado exitosamente", "id": nuevo_id}


@router.put("/{id_rol}")
def actualizar_rol(id_rol: int, rol: Rol, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "editar")
    exito = repo.actualizar(id_rol, rol)
    if not exito:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"mensaje": "Rol actualizado correctamente"}


@router.delete("/{id_rol}")
def eliminar_rol(id_rol: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "eliminar")
    exito = repo.eliminar(id_rol)
    if not exito:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"mensaje": "Rol eliminado correctamente"}

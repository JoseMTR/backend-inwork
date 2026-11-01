from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.rol_modulo import RolModulo
from app.repositories.rol_modulo_repo import RolModuloRepository

router = APIRouter(prefix="/rol-modulo", tags=["Permisos (rol_modulo)"])
repo = RolModuloRepository()


@router.get("/")
def listar_rol_modulo(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "leer")
    return repo.obtener_todos()


@router.get("/{id_rol_modulo}")
def obtener_rol_modulo(id_rol_modulo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "leer")
    rol_modulo = repo.obtener_por_id(id_rol_modulo)
    if not rol_modulo:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return rol_modulo


@router.post("/")
def crear_rol_modulo(rol_modulo: RolModulo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "crear")
    nuevo_id = repo.crear(rol_modulo)
    return {"mensaje": "Permiso registrado exitosamente", "id": nuevo_id}


@router.put("/{id_rol_modulo}")
def actualizar_rol_modulo(id_rol_modulo: int, rol_modulo: RolModulo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "editar")
    exito = repo.actualizar(id_rol_modulo, rol_modulo)
    if not exito:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return {"mensaje": "Permiso actualizado correctamente"}


@router.delete("/{id_rol_modulo}")
def eliminar_rol_modulo(id_rol_modulo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "eliminar")
    exito = repo.eliminar(id_rol_modulo)
    if not exito:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    return {"mensaje": "Permiso eliminado correctamente"}

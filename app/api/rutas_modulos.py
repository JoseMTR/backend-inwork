from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.modulo import Modulo
from app.repositories.modulo_repo import ModuloRepository

router = APIRouter(prefix="/modulos", tags=["Modulos"])
repo = ModuloRepository()


@router.get("/")
def listar_modulos(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "leer")
    return repo.obtener_todos()


@router.get("/{id_modulo}")
def obtener_modulo(id_modulo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "leer")
    modulo = repo.obtener_por_id(id_modulo)
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")
    return modulo


@router.post("/")
def crear_modulo(modulo: Modulo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "crear")
    nuevo_id = repo.crear(modulo)
    return {"mensaje": "Modulo registrado exitosamente", "id": nuevo_id}


@router.put("/{id_modulo}")
def actualizar_modulo(id_modulo: int, modulo: Modulo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "editar")
    exito = repo.actualizar(id_modulo, modulo)
    if not exito:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")
    return {"mensaje": "Modulo actualizado correctamente"}


@router.delete("/{id_modulo}")
def eliminar_modulo(id_modulo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "roles", "eliminar")
    exito = repo.eliminar(id_modulo)
    if not exito:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")
    return {"mensaje": "Modulo eliminado correctamente"}

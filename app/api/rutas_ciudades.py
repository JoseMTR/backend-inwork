from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.ciudad import Ciudad
from app.repositories.ciudad_repo import CiudadRepository

router = APIRouter(prefix="/ciudades", tags=["Ciudades"])
repo = CiudadRepository()


@router.get("/")
def listar_ciudades(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "leer")
    return repo.obtener_todos()


@router.get("/{id_ciudad}")
def obtener_ciudad(id_ciudad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "leer")
    ciudad = repo.obtener_por_id(id_ciudad)
    if not ciudad:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return ciudad


@router.post("/")
def crear_ciudad(ciudad: Ciudad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "crear")
    nuevo_id = repo.crear(ciudad)
    return {"mensaje": "Ciudad registrada exitosamente", "id": nuevo_id}


@router.put("/{id_ciudad}")
def actualizar_ciudad(id_ciudad: int, ciudad: Ciudad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "editar")
    exito = repo.actualizar(id_ciudad, ciudad)
    if not exito:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return {"mensaje": "Ciudad actualizada correctamente"}


@router.delete("/{id_ciudad}")
def eliminar_ciudad(id_ciudad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "eliminar")
    exito = repo.eliminar(id_ciudad)
    if not exito:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return {"mensaje": "Ciudad eliminada correctamente"}

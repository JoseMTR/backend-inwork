from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.habilidad import Habilidad
from app.repositories.habilidad_repo import HabilidadRepository

router = APIRouter(prefix="/habilidades", tags=["Habilidades"])
repo = HabilidadRepository()


@router.get("/")
def listar_habilidades(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "leer")
    return repo.obtener_todos()


@router.get("/{id_habilidad}")
def obtener_habilidad(id_habilidad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "leer")
    habilidad = repo.obtener_por_id(id_habilidad)
    if not habilidad:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")
    return habilidad


@router.post("/")
def crear_habilidad(habilidad: Habilidad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "crear")
    nuevo_id = repo.crear(habilidad)
    return {"mensaje": "Habilidad registrada exitosamente", "id": nuevo_id}


@router.put("/{id_habilidad}")
def actualizar_habilidad(id_habilidad: int, habilidad: Habilidad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "editar")
    exito = repo.actualizar(id_habilidad, habilidad)
    if not exito:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")
    return {"mensaje": "Habilidad actualizada correctamente"}


@router.delete("/{id_habilidad}")
def eliminar_habilidad(id_habilidad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "eliminar")
    exito = repo.eliminar(id_habilidad)
    if not exito:
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")
    return {"mensaje": "Habilidad eliminada correctamente"}

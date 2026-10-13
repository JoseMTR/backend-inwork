from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.calificacion import Calificacion
from app.repositories.calificacion_repo import CalificacionRepository

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])
repo = CalificacionRepository()


@router.get("/")
def listar_calificaciones(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "calificaciones", "leer")
    return repo.obtener_todos()


@router.get("/{id_calificacion}")
def obtener_calificacion(id_calificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "calificaciones", "leer")
    calificacion = repo.obtener_por_id(id_calificacion)
    if not calificacion:
        raise HTTPException(status_code=404, detail="Calificacion no encontrada")
    return calificacion


@router.post("/")
def crear_calificacion(calificacion: Calificacion, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "calificaciones", "crear")
    nuevo_id = repo.crear(calificacion, usuario["id_usuario"])
    return {"mensaje": "Calificacion registrada exitosamente", "id": nuevo_id}


@router.put("/{id_calificacion}")
def actualizar_calificacion(id_calificacion: int, calificacion: Calificacion, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "calificaciones", "editar")
    actual = repo.obtener_por_id(id_calificacion)
    if not actual:
        raise HTTPException(status_code=404, detail="Calificacion no encontrada")
    verificar_dueno(usuario, actual["id_calificador"])
    exito = repo.actualizar(id_calificacion, calificacion)
    if not exito:
        raise HTTPException(status_code=404, detail="Calificacion no encontrada")
    return {"mensaje": "Calificacion actualizada correctamente"}


@router.delete("/{id_calificacion}")
def eliminar_calificacion(id_calificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "calificaciones", "eliminar")
    actual = repo.obtener_por_id(id_calificacion)
    if not actual:
        raise HTTPException(status_code=404, detail="Calificacion no encontrada")
    verificar_dueno(usuario, actual["id_calificador"])
    exito = repo.eliminar(id_calificacion)
    if not exito:
        raise HTTPException(status_code=404, detail="Calificacion no encontrada")
    return {"mensaje": "Calificacion eliminada correctamente"}

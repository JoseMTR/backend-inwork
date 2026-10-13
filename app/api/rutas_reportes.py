from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, solo_staff, verificar_dueno, verificar_permiso
from app.models.reporte import Reporte, ReporteResolver
from app.repositories.reporte_repo import ReporteRepository

router = APIRouter(prefix="/reportes", tags=["Reportes"])
repo = ReporteRepository()


@router.get("/")
def listar_reportes(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "reportes", "leer")
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_reporte}")
def obtener_reporte(id_reporte: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "reportes", "leer")
    reporte = repo.obtener_por_id(id_reporte)
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    verificar_dueno(usuario, reporte["id_reportante"])
    return reporte


@router.post("/")
def crear_reporte(reporte: Reporte, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "reportes", "crear")
    nuevo_id = repo.crear(reporte, usuario["id_usuario"])
    return {"mensaje": "Reporte enviado exitosamente", "id": nuevo_id}


@router.put("/{id_reporte}")
def actualizar_reporte(id_reporte: int, reporte: Reporte, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "reportes", "editar")
    actual = repo.obtener_por_id(id_reporte)
    if not actual:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    verificar_dueno(usuario, actual["id_reportante"])
    if actual["estado_reporte"] != "pendiente":
        raise HTTPException(status_code=400, detail="El reporte ya esta siendo revisado")
    repo.actualizar(id_reporte, reporte)
    return {"mensaje": "Reporte actualizado correctamente"}


@router.put("/{id_reporte}/resolver")
def resolver_reporte(id_reporte: int, datos: ReporteResolver, usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    exito = repo.resolver(id_reporte, datos, usuario["id_usuario"])
    if not exito:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return {"mensaje": "Reporte actualizado"}


@router.delete("/{id_reporte}")
def eliminar_reporte(id_reporte: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "reportes", "eliminar")
    exito = repo.eliminar(id_reporte)
    if not exito:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return {"mensaje": "Reporte eliminado correctamente"}

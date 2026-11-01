from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.repositories.auditoria_repo import AuditoriaRepository

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])
repo = AuditoriaRepository()




@router.get("/")
def listar_auditoria(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "auditoria", "leer")
    return repo.obtener_todos()


@router.get("/{id_auditoria}")
def obtener_auditoria(id_auditoria: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "auditoria", "leer")
    registro = repo.obtener_por_id(id_auditoria)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro de auditoria no encontrado")
    return registro

from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.trabajo import Trabajo
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.trabajo_repo import TrabajoRepository

router = APIRouter(prefix="/trabajos", tags=["Trabajos"])
repo = TrabajoRepository()
auditoria = AuditoriaRepository()


@router.get("/")
def listar_trabajos(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "leer")
    return repo.obtener_todos()


# Esta ruta va ANTES de /{id_trabajo} para que "cercanos" no se confunda con un id
@router.get("/cercanos")
def trabajos_cercanos(latitud: float, longitud: float, radio_km: float = 10,
                      usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "leer")
    return repo.buscar_cercanos(latitud, longitud, radio_km)


@router.get("/{id_trabajo}")
def obtener_trabajo(id_trabajo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "leer")
    trabajo = repo.obtener_por_id(id_trabajo)
    if not trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return trabajo


@router.post("/")
def crear_trabajo(trabajo: Trabajo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "crear")
    nuevo_id = repo.crear(trabajo, usuario["id_usuario"])
    auditoria.registrar(usuario["id_usuario"], "trabajos", nuevo_id, "INSERT")
    return {"mensaje": "Trabajo publicado exitosamente", "id": nuevo_id}


@router.put("/{id_trabajo}")
def actualizar_trabajo(id_trabajo: int, trabajo: Trabajo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "editar")
    actual = repo.obtener_por_id(id_trabajo)
    if not actual:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    verificar_dueno(usuario, actual["id_cliente"])
    if actual["estado_trabajo"] != "publicado":
        raise HTTPException(status_code=400, detail="Solo se puede editar un trabajo que esta publicado")
    repo.actualizar(id_trabajo, trabajo)
    auditoria.registrar(usuario["id_usuario"], "trabajos", id_trabajo, "UPDATE")
    return {"mensaje": "Trabajo actualizado correctamente"}


@router.delete("/{id_trabajo}")
def eliminar_trabajo(id_trabajo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "eliminar")
    actual = repo.obtener_por_id(id_trabajo)
    if not actual:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    verificar_dueno(usuario, actual["id_cliente"])
    if actual["estado_trabajo"] == "asignado":
        raise HTTPException(status_code=400, detail="El trabajo tiene una contratacion activa, no se puede eliminar")
    repo.eliminar(id_trabajo)
    auditoria.registrar(usuario["id_usuario"], "trabajos", id_trabajo, "DELETE")
    return {"mensaje": "Trabajo eliminado correctamente"}

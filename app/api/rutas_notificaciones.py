from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, solo_staff, verificar_dueno, verificar_permiso
from app.models.notificacion import Notificacion
from app.repositories.notificacion_repo import NotificacionRepository

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])
repo = NotificacionRepository()



@router.get("/")
def listar_notificaciones(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "leer")
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_notificacion}")
def obtener_notificacion(id_notificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "leer")
    notificacion = repo.obtener_por_id(id_notificacion)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    verificar_dueno(usuario, notificacion["id_usuario"])
    return notificacion


@router.post("/")
def crear_notificacion(notificacion: Notificacion, usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    nuevo_id = repo.crear(notificacion)
    return {"mensaje": "Notificacion creada exitosamente", "id": nuevo_id}


@router.put("/{id_notificacion}")
def actualizar_notificacion(id_notificacion: int, notificacion: Notificacion,
                            usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    exito = repo.actualizar(id_notificacion, notificacion)
    if not exito:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    return {"mensaje": "Notificacion actualizada correctamente"}


@router.put("/{id_notificacion}/leer")
def marcar_como_leida(id_notificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "editar")
    notificacion = repo.obtener_por_id(id_notificacion)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    verificar_dueno(usuario, notificacion["id_usuario"])
    repo.marcar_leida(id_notificacion)
    return {"mensaje": "Notificacion marcada como leida"}


@router.delete("/{id_notificacion}")
def eliminar_notificacion(id_notificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "eliminar")
    notificacion = repo.obtener_por_id(id_notificacion)
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    verificar_dueno(usuario, notificacion["id_usuario"])
    repo.eliminar(id_notificacion)
    return {"mensaje": "Notificacion eliminada correctamente"}

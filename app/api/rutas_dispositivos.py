from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.dispositivo import Dispositivo
from app.repositories.dispositivo_repo import DispositivoRepository

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos"])
repo = DispositivoRepository()


@router.get("/")
def listar_dispositivos(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "leer")
    # Cada usuario ve solo los suyos; el staff ve todos
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_dispositivo}")
def obtener_dispositivo(id_dispositivo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "leer")
    dispositivo = repo.obtener_por_id(id_dispositivo)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    verificar_dueno(usuario, dispositivo["id_usuario"])
    return dispositivo


@router.post("/")
def crear_dispositivo(dispositivo: Dispositivo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "crear")
    nuevo_id = repo.crear(dispositivo, usuario["id_usuario"])
    return {"mensaje": "Dispositivo registrado exitosamente", "id": nuevo_id}


@router.put("/{id_dispositivo}")
def actualizar_dispositivo(id_dispositivo: int, dispositivo: Dispositivo, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "editar")
    actual = repo.obtener_por_id(id_dispositivo)
    if not actual:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    verificar_dueno(usuario, actual["id_usuario"])
    exito = repo.actualizar(id_dispositivo, dispositivo)
    if not exito:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return {"mensaje": "Dispositivo actualizado correctamente"}


@router.delete("/{id_dispositivo}")
def eliminar_dispositivo(id_dispositivo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "notificaciones", "eliminar")
    actual = repo.obtener_por_id(id_dispositivo)
    if not actual:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    verificar_dueno(usuario, actual["id_usuario"])
    exito = repo.eliminar(id_dispositivo)
    if not exito:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return {"mensaje": "Dispositivo eliminado correctamente"}

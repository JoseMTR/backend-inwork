from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.adjunto import Adjunto
from app.repositories.adjunto_repo import AdjuntoRepository

router = APIRouter(prefix="/adjuntos", tags=["Adjuntos"])
repo = AdjuntoRepository()


@router.get("/")
def listar_adjuntos(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "adjuntos", "leer")
    return repo.obtener_todos()


@router.get("/{id_adjunto}")
def obtener_adjunto(id_adjunto: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "adjuntos", "leer")
    adjunto = repo.obtener_por_id(id_adjunto)
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return adjunto


@router.post("/")
def crear_adjunto(adjunto: Adjunto, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "adjuntos", "crear")
    nuevo_id = repo.crear(adjunto, usuario["id_usuario"])
    return {"mensaje": "Adjunto registrado exitosamente", "id": nuevo_id}


@router.put("/{id_adjunto}")
def actualizar_adjunto(id_adjunto: int, adjunto: Adjunto, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "adjuntos", "editar")
    actual = repo.obtener_por_id(id_adjunto)
    if not actual:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    verificar_dueno(usuario, actual["id_subido_por"])
    exito = repo.actualizar(id_adjunto, adjunto)
    if not exito:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return {"mensaje": "Adjunto actualizado correctamente"}


@router.delete("/{id_adjunto}")
def eliminar_adjunto(id_adjunto: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "adjuntos", "eliminar")
    actual = repo.obtener_por_id(id_adjunto)
    if not actual:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    verificar_dueno(usuario, actual["id_subido_por"])
    exito = repo.eliminar(id_adjunto)
    if not exito:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return {"mensaje": "Adjunto eliminado correctamente"}

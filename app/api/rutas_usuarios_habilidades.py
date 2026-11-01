from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.usuario_habilidad import UsuarioHabilidad
from app.repositories.usuario_habilidad_repo import UsuarioHabilidadRepository

router = APIRouter(prefix="/usuarios-habilidades", tags=["Habilidades de usuarios"])
repo = UsuarioHabilidadRepository()


@router.get("/")
def listar_usuarios_habilidades(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "leer")
    return repo.obtener_todos()


@router.get("/{id_usuario_habilidad}")
def obtener_usuario_habilidad(id_usuario_habilidad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "leer")
    usuario_habilidad = repo.obtener_por_id(id_usuario_habilidad)
    if not usuario_habilidad:
        raise HTTPException(status_code=404, detail="Habilidad del usuario no encontrada")
    return usuario_habilidad


@router.post("/")
def crear_usuario_habilidad(usuario_habilidad: UsuarioHabilidad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "crear")
    nuevo_id = repo.crear(usuario_habilidad, usuario["id_usuario"])
    return {"mensaje": "Habilidad del usuario registrada exitosamente", "id": nuevo_id}


@router.put("/{id_usuario_habilidad}")
def actualizar_usuario_habilidad(id_usuario_habilidad: int, usuario_habilidad: UsuarioHabilidad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "editar")
    actual = repo.obtener_por_id(id_usuario_habilidad)
    if not actual:
        raise HTTPException(status_code=404, detail="Habilidad del usuario no encontrada")
    verificar_dueno(usuario, actual["id_usuario"])
    exito = repo.actualizar(id_usuario_habilidad, usuario_habilidad)
    if not exito:
        raise HTTPException(status_code=404, detail="Habilidad del usuario no encontrada")
    return {"mensaje": "Habilidad del usuario actualizada correctamente"}


@router.delete("/{id_usuario_habilidad}")
def eliminar_usuario_habilidad(id_usuario_habilidad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "usuarios", "eliminar")
    actual = repo.obtener_por_id(id_usuario_habilidad)
    if not actual:
        raise HTTPException(status_code=404, detail="Habilidad del usuario no encontrada")
    verificar_dueno(usuario, actual["id_usuario"])
    exito = repo.eliminar(id_usuario_habilidad)
    if not exito:
        raise HTTPException(status_code=404, detail="Habilidad del usuario no encontrada")
    return {"mensaje": "Habilidad del usuario eliminada correctamente"}

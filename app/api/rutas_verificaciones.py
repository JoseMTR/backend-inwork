from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, solo_staff, verificar_dueno, verificar_permiso
from app.models.verificacion_identidad import VerificacionIdentidad, VerificacionRevisar
from app.repositories.verificacion_identidad_repo import VerificacionIdentidadRepository

router = APIRouter(prefix="/verificaciones-identidad", tags=["Verificacion de identidad"])
repo = VerificacionIdentidadRepository()


@router.get("/")
def listar_verificaciones(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "verificaciones", "leer")
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_verificacion}")
def obtener_verificacion(id_verificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "verificaciones", "leer")
    verificacion = repo.obtener_por_id(id_verificacion)
    if not verificacion:
        raise HTTPException(status_code=404, detail="Verificacion no encontrada")
    verificar_dueno(usuario, verificacion["id_usuario"])
    return verificacion


@router.post("/")
def crear_verificacion(verificacion: VerificacionIdentidad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "verificaciones", "crear")
    nuevo_id = repo.crear(verificacion, usuario["id_usuario"])
    return {"mensaje": "Documentos enviados. Un moderador los revisara.", "id": nuevo_id}


@router.put("/{id_verificacion}")
def actualizar_verificacion(id_verificacion: int, verificacion: VerificacionIdentidad,
                            usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "verificaciones", "editar")
    actual = repo.obtener_por_id(id_verificacion)
    if not actual:
        raise HTTPException(status_code=404, detail="Verificacion no encontrada")
    verificar_dueno(usuario, actual["id_usuario"])
    if actual["estado_verificacion"] != "pendiente":
        raise HTTPException(status_code=400, detail="La verificacion ya fue revisada")
    repo.actualizar(id_verificacion, verificacion)
    return {"mensaje": "Verificacion actualizada correctamente"}


@router.put("/{id_verificacion}/revisar")
def revisar_verificacion(id_verificacion: int, datos: VerificacionRevisar,
                         usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    exito = repo.revisar(id_verificacion, datos, usuario["id_usuario"])
    if not exito:
        raise HTTPException(status_code=404, detail="Verificacion no encontrada")
    return {"mensaje": f"Verificacion {datos.estado_verificacion}"}


@router.delete("/{id_verificacion}")
def eliminar_verificacion(id_verificacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "verificaciones", "eliminar")
    exito = repo.eliminar(id_verificacion)
    if not exito:
        raise HTTPException(status_code=404, detail="Verificacion no encontrada")
    return {"mensaje": "Verificacion eliminada correctamente"}

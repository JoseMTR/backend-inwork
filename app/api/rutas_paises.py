from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.pais import Pais
from app.repositories.pais_repo import PaisRepository

router = APIRouter(prefix="/paises", tags=["Paises"])
repo = PaisRepository()


@router.get("/")
def listar_paises(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "leer")
    return repo.obtener_todos()


@router.get("/{id_pais}")
def obtener_pais(id_pais: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "leer")
    pais = repo.obtener_por_id(id_pais)
    if not pais:
        raise HTTPException(status_code=404, detail="Pais no encontrado")
    return pais


@router.post("/")
def crear_pais(pais: Pais, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "crear")
    nuevo_id = repo.crear(pais)
    return {"mensaje": "Pais registrado exitosamente", "id": nuevo_id}


@router.put("/{id_pais}")
def actualizar_pais(id_pais: int, pais: Pais, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "editar")
    exito = repo.actualizar(id_pais, pais)
    if not exito:
        raise HTTPException(status_code=404, detail="Pais no encontrado")
    return {"mensaje": "Pais actualizado correctamente"}


@router.delete("/{id_pais}")
def eliminar_pais(id_pais: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ubicacion", "eliminar")
    exito = repo.eliminar(id_pais)
    if not exito:
        raise HTTPException(status_code=404, detail="Pais no encontrado")
    return {"mensaje": "Pais eliminado correctamente"}

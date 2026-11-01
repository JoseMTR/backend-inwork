from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_permiso
from app.models.categoria import Categoria
from app.repositories.categoria_repo import CategoriaRepository

router = APIRouter(prefix="/categorias", tags=["Categorias"])
repo = CategoriaRepository()


@router.get("/")
def listar_categorias(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "leer")
    return repo.obtener_todos()


@router.get("/{id_categoria}")
def obtener_categoria(id_categoria: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "leer")
    categoria = repo.obtener_por_id(id_categoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return categoria


@router.post("/")
def crear_categoria(categoria: Categoria, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "crear")
    nuevo_id = repo.crear(categoria)
    return {"mensaje": "Categoria registrada exitosamente", "id": nuevo_id}


@router.put("/{id_categoria}")
def actualizar_categoria(id_categoria: int, categoria: Categoria, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "editar")
    exito = repo.actualizar(id_categoria, categoria)
    if not exito:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return {"mensaje": "Categoria actualizada correctamente"}


@router.delete("/{id_categoria}")
def eliminar_categoria(id_categoria: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "categorias", "eliminar")
    exito = repo.eliminar(id_categoria)
    if not exito:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    return {"mensaje": "Categoria eliminada correctamente"}

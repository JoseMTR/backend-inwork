from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.trabajo_habilidad import TrabajoHabilidad
from app.repositories.trabajo_habilidad_repo import TrabajoHabilidadRepository
from app.repositories.trabajo_repo import TrabajoRepository

router = APIRouter(prefix="/trabajos-habilidades", tags=["Habilidades de trabajos"])
repo = TrabajoHabilidadRepository()
trabajo_repo = TrabajoRepository()


def verificar_dueno_del_trabajo(usuario: dict, id_trabajo: int):
    trabajo = trabajo_repo.obtener_por_id(id_trabajo)
    if not trabajo:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    verificar_dueno(usuario, trabajo["id_cliente"])


@router.get("/")
def listar_trabajos_habilidades(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "leer")
    return repo.obtener_todos()


@router.get("/trabajo/{id_trabajo}")
def habilidades_de_un_trabajo(id_trabajo: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "leer")
    return repo.obtener_por_trabajo(id_trabajo)


@router.get("/{id_trabajo_habilidad}")
def obtener_trabajo_habilidad(id_trabajo_habilidad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "leer")
    registro = repo.obtener_por_id(id_trabajo_habilidad)
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return registro


@router.post("/")
def crear_trabajo_habilidad(datos: TrabajoHabilidad, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "crear")
    verificar_dueno_del_trabajo(usuario, datos.id_trabajo)
    nuevo_id = repo.crear(datos)
    return {"mensaje": "Habilidad agregada al trabajo", "id": nuevo_id}


@router.put("/{id_trabajo_habilidad}")
def actualizar_trabajo_habilidad(id_trabajo_habilidad: int, datos: TrabajoHabilidad,
                                 usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "editar")
    actual = repo.obtener_por_id(id_trabajo_habilidad)
    if not actual:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    verificar_dueno_del_trabajo(usuario, actual["id_trabajo"])
    repo.actualizar(id_trabajo_habilidad, datos)
    return {"mensaje": "Habilidad del trabajo actualizada correctamente"}


@router.delete("/{id_trabajo_habilidad}")
def eliminar_trabajo_habilidad(id_trabajo_habilidad: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "trabajos", "eliminar")
    actual = repo.obtener_por_id(id_trabajo_habilidad)
    if not actual:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    verificar_dueno_del_trabajo(usuario, actual["id_trabajo"])
    repo.eliminar(id_trabajo_habilidad)
    return {"mensaje": "Habilidad quitada del trabajo"}

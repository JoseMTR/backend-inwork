from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, solo_staff, verificar_dueno, verificar_permiso
from app.models.contratacion import Contratacion, ContratacionEstado
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.contratacion_repo import ContratacionRepository
from app.repositories.custodia_repo import CustodiaRepository

router = APIRouter(prefix="/contrataciones", tags=["Contrataciones"])
repo = ContratacionRepository()
custodia_repo = CustodiaRepository()
auditoria = AuditoriaRepository()


def buscar_contratacion(id_contratacion: int, usuario: dict):
    contratacion = repo.obtener_por_id(id_contratacion)
    if not contratacion:
        raise HTTPException(status_code=404, detail="Contratacion no encontrada")
    participantes = (contratacion["id_cliente"], contratacion["id_trabajador"])
    if usuario["id_usuario"] not in participantes and not es_staff(usuario):
        raise HTTPException(status_code=403, detail="No participas en esta contratacion")
    return contratacion


def crear_custodia(id_contratacion: int):
    datos = repo.datos_para_custodia(id_contratacion)
    return custodia_repo.crear(datos)


@router.get("/")
def listar_contrataciones(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "contrataciones", "leer")
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_contratacion}")
def obtener_contratacion(id_contratacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "contrataciones", "leer")
    return buscar_contratacion(id_contratacion, usuario)


@router.post("/")
def crear_contratacion(contratacion: Contratacion, usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    nuevo_id = repo.crear(contratacion)
    auditoria.registrar(usuario["id_usuario"], "contrataciones", nuevo_id, "INSERT")
    creada, respuesta = crear_custodia(nuevo_id)
    return {"mensaje": "Contratacion creada", "id": nuevo_id, "custodia_creada": creada, "api_pagos": respuesta}


@router.put("/{id_contratacion}")
def actualizar_contratacion(id_contratacion: int, datos: ContratacionEstado,
                            usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    exito = repo.actualizar(id_contratacion, datos.estado_contratacion)
    if not exito:
        raise HTTPException(status_code=404, detail="Contratacion no encontrada")
    auditoria.registrar(usuario["id_usuario"], "contrataciones", id_contratacion, "UPDATE")
    return {"mensaje": "Contratacion actualizada correctamente"}


@router.delete("/{id_contratacion}")
def eliminar_contratacion(id_contratacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    solo_staff(usuario)
    exito = repo.eliminar(id_contratacion)
    if not exito:
        raise HTTPException(status_code=404, detail="Contratacion no encontrada")
    auditoria.registrar(usuario["id_usuario"], "contrataciones", id_contratacion, "DELETE")
    return {"mensaje": "Contratacion eliminada correctamente"}



@router.get("/{id_contratacion}/pago")
def estado_del_pago(id_contratacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    """Consulta en la API de pagos como va el dinero de esta contratacion."""
    verificar_permiso(usuario, "contrataciones", "leer")
    buscar_contratacion(id_contratacion, usuario)
    conectado, custodia = custodia_repo.obtener_por_contratacion(id_contratacion)
    if not conectado:
        raise HTTPException(status_code=503, detail="No se pudo conectar con la API de pagos")
    if not custodia:
        raise HTTPException(status_code=404, detail="Esta contratacion no tiene custodia de pago")
    return custodia


@router.post("/{id_contratacion}/custodia")
def reintentar_custodia(id_contratacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    """Si al aceptar la oferta fallo la API de pagos, se vuelve a intentar crear la custodia."""
    contratacion = buscar_contratacion(id_contratacion, usuario)
    verificar_dueno(usuario, contratacion["id_cliente"])
    if contratacion["estado_contratacion"] != "activa":
        raise HTTPException(status_code=400, detail="La contratacion no esta activa")
    creada, respuesta = crear_custodia(id_contratacion)
    if not creada:
        raise HTTPException(status_code=400, detail=respuesta.get("mensaje", "No se pudo crear la custodia"))
    return {"mensaje": "Custodia creada en la API de pagos. El cliente ya puede pagar.", "custodia": respuesta}


@router.post("/{id_contratacion}/finalizar")
def finalizar_contratacion(id_contratacion: int, usuario: dict = Depends(obtener_usuario_actual)):

    verificar_permiso(usuario, "contrataciones", "editar")
    contratacion = buscar_contratacion(id_contratacion, usuario)
    verificar_dueno(usuario, contratacion["id_cliente"])
    if contratacion["estado_contratacion"] != "activa":
        raise HTTPException(status_code=400, detail="La contratacion no esta activa")

    conectado, custodia = custodia_repo.obtener_por_contratacion(id_contratacion)
    if not conectado:
        raise HTTPException(status_code=503, detail="No se pudo conectar con la API de pagos")
    if not custodia or custodia["estado_custodia"] != "liberado":
        raise HTTPException(
            status_code=400,
            detail="Todavia no se puede finalizar: el cliente y el trabajador deben confirmar "
                   "en la API de pagos para que se libere el dinero"
        )

    repo.finalizar(contratacion)
    auditoria.registrar(usuario["id_usuario"], "contrataciones", id_contratacion, "UPDATE")
    return {"mensaje": "Contratacion finalizada. Ya se pueden calificar."}


@router.post("/{id_contratacion}/cancelar")
def cancelar_contratacion(id_contratacion: int, usuario: dict = Depends(obtener_usuario_actual)):
    """Cliente o trabajador cancelan. No se puede si hay dinero guardado en la custodia."""
    verificar_permiso(usuario, "contrataciones", "editar")
    contratacion = buscar_contratacion(id_contratacion, usuario)
    if contratacion["estado_contratacion"] != "activa":
        raise HTTPException(status_code=400, detail="La contratacion no esta activa")

    conectado, custodia = custodia_repo.obtener_por_contratacion(id_contratacion)
    if not conectado:
        raise HTTPException(status_code=503, detail="No se pudo conectar con la API de pagos")
    if custodia:
        if custodia["estado_custodia"] in ("asegurado", "en_disputa", "liberado"):
            raise HTTPException(
                status_code=400,
                detail="Hay dinero en custodia. Para cancelar, abre una disputa en la API de pagos"
            )
        if custodia["estado_custodia"] == "pendiente_pago":
            custodia_repo.cancelar(custodia["id_custodia"])

    repo.cancelar(contratacion, usuario["id_usuario"])
    auditoria.registrar(usuario["id_usuario"], "contrataciones", id_contratacion, "UPDATE")
    return {"mensaje": "Contratacion cancelada. El trabajo vuelve a estar publicado."}

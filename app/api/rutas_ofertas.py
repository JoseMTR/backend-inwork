from fastapi import APIRouter, Depends, HTTPException

from app.core.seguridad import es_staff, obtener_usuario_actual, verificar_dueno, verificar_permiso
from app.models.oferta import Oferta
from app.repositories.auditoria_repo import AuditoriaRepository
from app.repositories.contratacion_repo import ContratacionRepository
from app.repositories.custodia_repo import CustodiaRepository
from app.repositories.oferta_repo import OfertaRepository

router = APIRouter(prefix="/ofertas", tags=["Ofertas"])
repo = OfertaRepository()
contratacion_repo = ContratacionRepository()
custodia_repo = CustodiaRepository()
auditoria = AuditoriaRepository()


@router.get("/")
def listar_ofertas(usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ofertas", "leer")
    if es_staff(usuario):
        return repo.obtener_todos()
    return repo.obtener_por_usuario(usuario["id_usuario"])


@router.get("/{id_oferta}")
def obtener_oferta(id_oferta: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ofertas", "leer")
    oferta = repo.obtener_por_id(id_oferta)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    # La ve quien oferto, el dueno del trabajo o el staff
    if usuario["id_usuario"] not in (oferta["id_trabajador"], oferta["id_cliente"]) and not es_staff(usuario):
        raise HTTPException(status_code=403, detail="No puedes ver esta oferta")
    return oferta


@router.post("/")
def crear_oferta(oferta: Oferta, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ofertas", "crear")
    nuevo_id = repo.crear(oferta, usuario["id_usuario"])
    auditoria.registrar(usuario["id_usuario"], "ofertas", nuevo_id, "INSERT")
    return {"mensaje": "Oferta enviada exitosamente", "id": nuevo_id}


@router.put("/{id_oferta}")
def actualizar_oferta(id_oferta: int, oferta: Oferta, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ofertas", "editar")
    actual = repo.obtener_por_id(id_oferta)
    if not actual:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    verificar_dueno(usuario, actual["id_trabajador"])
    if actual["estado_oferta"] != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se puede editar una oferta pendiente")
    repo.actualizar(id_oferta, oferta)
    return {"mensaje": "Oferta actualizada correctamente"}


@router.delete("/{id_oferta}")
def eliminar_oferta(id_oferta: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ofertas", "eliminar")
    actual = repo.obtener_por_id(id_oferta)
    if not actual:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    verificar_dueno(usuario, actual["id_trabajador"])
    if actual["estado_oferta"] == "aceptada":
        raise HTTPException(status_code=400, detail="No se puede eliminar una oferta aceptada")
    repo.eliminar(id_oferta)
    return {"mensaje": "Oferta eliminada correctamente"}


@router.post("/{id_oferta}/aceptar")
def aceptar_oferta(id_oferta: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "contrataciones", "crear")
    oferta = repo.obtener_por_id(id_oferta)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    verificar_dueno(usuario, oferta["id_cliente"])
    if oferta["estado_oferta"] != "pendiente":
        raise HTTPException(status_code=400, detail="La oferta ya no esta pendiente")
    if oferta["estado_trabajo"] != "publicado":
        raise HTTPException(status_code=400, detail="El trabajo ya no esta publicado")

    id_contratacion = repo.aceptar(oferta)
    auditoria.registrar(usuario["id_usuario"], "contrataciones", id_contratacion, "INSERT")

    datos = contratacion_repo.datos_para_custodia(id_contratacion)
    creada, respuesta = custodia_repo.crear(datos)

    if creada:
        return {
            "mensaje": "Oferta aceptada. Se creo el contrato y la custodia del pago. Ya puedes pagar.",
            "id_contratacion": id_contratacion,
            "custodia": respuesta,
        }
    return {
        "mensaje": "Oferta aceptada y contrato creado, pero NO se pudo crear la custodia del pago.",
        "id_contratacion": id_contratacion,
        "error_api_pagos": respuesta,
        "solucion": f"Intenta de nuevo con POST /contrataciones/{id_contratacion}/custodia",
    }


@router.post("/{id_oferta}/retirar")
def retirar_oferta(id_oferta: int, usuario: dict = Depends(obtener_usuario_actual)):
    verificar_permiso(usuario, "ofertas", "editar")
    oferta = repo.obtener_por_id(id_oferta)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    verificar_dueno(usuario, oferta["id_trabajador"])
    if oferta["estado_oferta"] != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se puede retirar una oferta pendiente")
    repo.retirar(id_oferta)
    return {"mensaje": "Oferta retirada"}

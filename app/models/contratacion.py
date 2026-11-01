from pydantic import BaseModel
from typing import Optional


class Contratacion(BaseModel):
    id_contratacion: Optional[int] = None
    id_trabajo: int
    id_cliente: int
    id_trabajador: int
    id_oferta: int


class ContratacionEstado(BaseModel):
    estado_contratacion: str   

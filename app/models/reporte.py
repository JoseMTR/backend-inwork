from pydantic import BaseModel
from typing import Optional


class Reporte(BaseModel):
    id_reporte: Optional[int] = None
    id_reportado: int
    id_trabajo: int
    motivo: str      
    descripcion: str


class ReporteResolver(BaseModel):
    estado_reporte: str  # en_revision, resuelto o rechazado
    resolucion: Optional[str] = None

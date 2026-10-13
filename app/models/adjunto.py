from pydantic import BaseModel
from typing import Optional


class Adjunto(BaseModel):
    id_adjunto: Optional[int] = None
    tipo_entidad: str        # trabajo, mensaje o reporte
    id_entidad: int
    url: str
    tipo_mime: Optional[str] = None

from pydantic import BaseModel
from typing import Optional


class TrabajoHabilidad(BaseModel):
    id_trabajo_habilidad: Optional[int] = None
    id_trabajo: int
    id_habilidad: int

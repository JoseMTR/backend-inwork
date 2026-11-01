from pydantic import BaseModel
from typing import Optional


class Habilidad(BaseModel):
    id_habilidad: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None

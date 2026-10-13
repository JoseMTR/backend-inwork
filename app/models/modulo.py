from pydantic import BaseModel
from typing import Optional


class Modulo(BaseModel):
    id_modulo: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None

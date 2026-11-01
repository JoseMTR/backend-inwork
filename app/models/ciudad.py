from pydantic import BaseModel
from typing import Optional


class Ciudad(BaseModel):
    id_ciudad: Optional[int] = None
    id_pais: int
    nombre: str

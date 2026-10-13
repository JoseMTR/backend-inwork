from pydantic import BaseModel
from typing import Optional


class Pais(BaseModel):
    id_pais: Optional[int] = None
    nombre: str

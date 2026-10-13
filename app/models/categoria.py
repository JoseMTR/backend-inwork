from pydantic import BaseModel
from typing import Optional


class Categoria(BaseModel):
    id_categoria: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None

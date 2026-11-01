from pydantic import BaseModel
from typing import Optional


class Notificacion(BaseModel):
    id_notificacion: Optional[int] = None
    id_usuario: int
    tipo: str                  
    titulo: str
    contenido: Optional[str] = None
    id_referencia: Optional[int] = None

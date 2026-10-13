from pydantic import BaseModel
from typing import Optional


class Calificacion(BaseModel):
    id_calificacion: Optional[int] = None
    id_calificado: int
    id_trabajo: int
    puntuacion: int          # de 1 a 5
    comentario: Optional[str] = None

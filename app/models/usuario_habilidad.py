from pydantic import BaseModel
from typing import Optional


class UsuarioHabilidad(BaseModel):
    id_usuario_habilidad: Optional[int] = None
    id_habilidad: int
    anios_experiencia: int

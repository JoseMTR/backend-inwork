from pydantic import BaseModel
from typing import Optional


class RolModulo(BaseModel):
    id_rol_modulo: Optional[int] = None
    id_rol: int
    id_modulo: int
    puede_crear: bool
    puede_leer: bool
    puede_editar: bool
    puede_eliminar: bool

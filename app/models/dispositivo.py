from pydantic import BaseModel
from typing import Optional


class Dispositivo(BaseModel):
    id_dispositivo: Optional[int] = None
    token_push: str
    plataforma: str     

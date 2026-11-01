from pydantic import BaseModel
from typing import Optional


class Mensaje(BaseModel):
    id_mensaje: Optional[int] = None
    id_chat: int
    mensaje: str

from pydantic import BaseModel
from typing import Optional


class Chat(BaseModel):
    id_chat: Optional[int] = None
    id_trabajo: int
    id_cliente: int
    id_trabajador: int

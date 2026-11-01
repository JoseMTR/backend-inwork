from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TokenUsuario(BaseModel):
    id_token: Optional[int] = None
    id_usuario: int
    tipo: str  
    token: str          
    expira: datetime
    usado: bool = False

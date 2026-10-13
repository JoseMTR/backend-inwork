from pydantic import BaseModel
from typing import Optional


class Oferta(BaseModel):
    id_oferta: Optional[int] = None
    id_trabajo: int
    valor_oferta: float
    moneda: str = "COP"
    mensaje: Optional[str] = None

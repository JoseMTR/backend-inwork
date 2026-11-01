from pydantic import BaseModel
from typing import Optional


class VerificacionIdentidad(BaseModel):
    id_verificacion: Optional[int] = None
    url_documento_frente: str
    url_documento_reverso: Optional[str] = None
    url_selfie: str


class VerificacionRevisar(BaseModel):
    estado_verificacion: str    
    observacion: Optional[str] = None

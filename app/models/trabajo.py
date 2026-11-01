from datetime import date, time
from pydantic import BaseModel
from typing import Optional


class Trabajo(BaseModel):
    id_trabajo: Optional[int] = None
    id_categoria: int
    id_ciudad: int
    titulo: str
    descripcion: str
    direccion: Optional[str] = None
    latitud: float
    longitud: float
    fecha_trabajo: date
    hora_inicio: time
    hora_fin: time
    presupuesto: float
    moneda: str = "COP"

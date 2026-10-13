from datetime import date
from pydantic import BaseModel
from typing import Optional


class UsuarioRegistro(BaseModel):
    id_ciudad: Optional[int] = None
    nombre: str
    apellido: str
    correo: str
    password: str
    telefono: str
    tipo_identificacion: str    
    numero_identificacion: str
    fecha_nacimiento: date
    foto_perfil: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None


class UsuarioActualizar(BaseModel):
    id_ciudad: Optional[int] = None
    nombre: str
    apellido: str
    telefono: str
    foto_perfil: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None


class CambiarRol(BaseModel):
    id_rol: int


class Login(BaseModel):
    correo: str
    password: str


class CambiarPassword(BaseModel):
    password_actual: str
    password_nueva: str

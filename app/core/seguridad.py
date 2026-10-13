import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.repositories.rol_modulo_repo import RolModuloRepository
from app.repositories.usuario_repo import UsuarioRepository

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esta_clave")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

ROL_ADMIN = 1
ROL_MODERADOR = 2
ROL_USUARIO = 3

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

usuario_repo = UsuarioRepository()
rol_modulo_repo = RolModuloRepository()

def encriptar_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_encriptada: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_encriptada.encode("utf-8"))
    except ValueError:
        return False


def crear_token(usuario: dict) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    datos = {"sub": str(usuario["id_usuario"]), "rol": usuario["id_rol"], "exp": expira}
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """Se usa en las rutas protegidas: usuario: dict = Depends(obtener_usuario_actual)"""
    try:
        datos = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(datos["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token expiro, inicia sesion de nuevo")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")

    usuario = usuario_repo.obtener_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=401, detail="El usuario ya no existe")
    return usuario


def es_admin(usuario: dict) -> bool:
    return usuario["id_rol"] == ROL_ADMIN


def es_staff(usuario: dict) -> bool:
    return usuario["id_rol"] in (ROL_ADMIN, ROL_MODERADOR)


def verificar_permiso(usuario: dict, modulo: str, accion: str):

    if es_admin(usuario):
        return
    permiso = rol_modulo_repo.obtener_permiso(usuario["id_rol"], modulo)
    if not permiso or not permiso["puede_" + accion]:
        raise HTTPException(status_code=403, detail=f"No tienes permiso para {accion} en {modulo}")


def verificar_dueno(usuario: dict, id_dueno: int):
    """Solo el dueno del registro (o el staff) puede modificarlo."""
    if usuario["id_usuario"] != id_dueno and not es_staff(usuario):
        raise HTTPException(status_code=403, detail="Este registro no te pertenece")


def solo_staff(usuario: dict):
    if not es_staff(usuario):
        raise HTTPException(status_code=403, detail="Solo un administrador o moderador puede hacer esto")
